# Lambda function Implementation of an async Strands Agent that gets invoked via a task from SQS
import json
import uuid
import boto3
import logging
import os
from strands import Agent
from strands.models import BedrockModel
# Local imports
import human_approval

logger = logging.getLogger(__name__)

MEMORY_TABLE = os.environ.get('MEMORY_TABLE', 'dev-agent-memory-store')

def save_to_agent_memory(session_id, messages):
    # Put messages against the session_id in memory store
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(MEMORY_TABLE)
    logger.info(f"Saving {len(messages)} messages to agent memory for session_id {session_id}")
    table.put_item(Item={'session_id': session_id, 'messages': messages})
    return True

def load_from_agent_memory(session_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(MEMORY_TABLE)
    logger.info(f"Loading messages from agent memory for session_id {session_id}")
    response = table.get_item(Key={'session_id': session_id})
    item = response.get('Item', {})
    messages = item.get('messages', [])
    logger.info(f"Loaded {len(messages)} messages from agent memory for session_id {session_id}")
    return messages

def prepare(task) -> Agent:
    type = task.get('type', None)
    assert type is not None, "Task type is not specified"
    assert type in ["new", "existing"], "Task type is not supported, must be `new` or `existing`"
    logger.info(f"Preparing agent for {type} task")
    if type == "new":
        # Structure of a new task
        # {
        #     'type': 'new',
        #     'body': {
        #         'task': 'new task description',
        #     }
        # }
        task_body = task.get('body', None)
        assert task_body is not None, "Task body is not specified"
        task_description = task_body.get('task', None)
        assert task_description is not None, "Task description is not specified"
        # Create a new session_id UUID
        session_id = str(uuid.uuid4())
        logger.info(f"New session_id: {session_id}")
        # Create messages
        messages = []
        return session_id, messages, task_description
    
    if type == "existing":
        #  Result of successful tool execution
        # {
        #     'session_id': 'id of the session',
        #     'type': 'existing',
        #     'toolName': 'name of the tool',
        #     'body': [{
        #         'toolResult': {
        #             'toolUseId': 'id of the tool that was used',
        #             'status': 'success|error',
        #             'content': [{'text': 'tool result content | error message'}]
        #         }
        #     }]
        # }

        session_id = task.get('session_id', None)
        assert session_id is not None, "Session ID is not specified"
        logger.info(f"Using existing session_id: {session_id}")
        # Load messages from agent memory
        messages = load_from_agent_memory(session_id)
        if messages and len(messages) > 1:
            # Remove the last message from the messages
            messages = messages[:-1]
            # Append the tool result to the messages
            logger.info(f"Appending tool result to messages: {task.get('body', [{}])}")
            messages.append({
                "role": "user",
                "content": task.get('body', [{}])
            })
            return session_id, messages, "Continue"
        else:
            logger.info("No messages found in agent memory, starting a new conversation")
            return session_id, [], "Continue"
    logger.error(f"Unknown task type: {type}")
    return str(uuid.uuid4()), [], "Hello, how can you help?"

def lambda_handler(event, context):
    logger.info(f"Received event: {event}")
        
    # Even when processing a single message, AWS Lambda still wraps it in a Records array
    if not event.get('Records') or len(event['Records']) == 0:
        logger.error("No records found in the event")
        return {
            'statusCode': 400,
            'body': json.dumps('No SQS message records found in the event')
        }
    
    # Extract the first (and only) message
    record = json.loads(event['Records'][0]['body'])
    session_id, history, prompt  = prepare(record)

    # Create model
    model = BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        region_name="us-east-1"
    )

    # Create agent
    agent = Agent(
        model=model,
        tools=[human_approval],
        messages=history,
    )
    
    result = agent(prompt, session_id=session_id)

    if result.state.get("stop_event_loop", False):
        logger.info("Agent needs to wait for tool result. Saving state and sleeping.")
        save_to_agent_memory(session_id, agent.messages)

    logger.info(str(result))


