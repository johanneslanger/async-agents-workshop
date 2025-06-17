# Lambda function Implementation of an async Strands Agent that gets invoked via a task from SQS
import json
import uuid
import boto3
import logging
import os
from strands import Agent, tool
from strands.models import BedrockModel

import publish_evaluation

logger = logging.getLogger(__name__)

MEMORY_TABLE = os.environ.get('MEMORY_TABLE', 'dev-agent-memory-store')
CALLBACK_SQS_URL = os.environ.get('CALLBACK_SQS_URL', None)
AGENT_NAME = 'evaluator-agent'

def save_to_agent_memory(session_id, messages, parent=None):
    # Put messages () against the session_id in memory store
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(MEMORY_TABLE)
    logger.info(f"Saving {len(messages)} messages to agent memory for session_id {session_id}")
    agent_memory_object = {
        'session_id': session_id, 
        'agent_name': AGENT_NAME,
        'messages': messages,
    }
    if parent:
        agent_memory_object['parent'] = parent
    
    table.put_item(Item=agent_memory_object)
    return True

def load_from_agent_memory(session_id):
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(MEMORY_TABLE)
    logger.info(f"Loading messages from agent memory for session_id {session_id}")
    # Load messages from agent memory of given session_id for this AGENT_NAME
    response = table.get_item(Key={'session_id': session_id, 'agent_name': AGENT_NAME})
    item = response.get('Item', {})
    messages = item.get('messages', [])
    parent = item.get('parent', None)
    logger.info(f"Loaded {len(messages)} messages from agent memory of {AGENT_NAME} for session_id: {session_id}")
    return messages, parent

def prepare(task) -> Agent:
    type = task.get('type', None)
    parent = task.get('parent',None)
    assert type is not None, "Task type is not specified"
    assert type in ["new", "existing"], "Task type is not supported, must be `new` or `existing`"
    logger.info(f"Preparing agent for {type} task")
    if type == "new":
        # Structure of a new task
        # {
        #     'type': 'new',
        #     'body': {
        #         'task': 'new task description',
        #     },
        #     'parent': {
        #         'agent_name': 'name of the agent who requested this task',
        #         'session_id': 'id of the session that the parent is carrying',
        #         'callback_sqs': 'SQS queue url to report the completion of the task',
        #         'tool_use_id': 'id of the tool that was initiaed to call this agent'
        #     }
        # }
        task_body = task.get('body', None)
        assert task_body is not None, "Task body is not specified"
        task_description = task_body.get('task', None)
        assert task_description is not None, "Task description is not specified"

        if parent:
            session_id = parent['session_id']
            logger.info(f"Reusing parent session_id: {session_id}")
        else:
            # Create a new session_id UUID
            session_id = str(uuid.uuid4())
            logger.info(f"New session_id: {session_id}")
            parent = {
                'agent_name': AGENT_NAME,
                'session_id': session_id,
                'callback_sqs': CALLBACK_SQS_URL
            }
        # Create messages
        messages = []
        return session_id, messages, task_description, parent
    
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
        messages, parent = load_from_agent_memory(session_id)
        if messages and len(messages) > 1:
            # Remove the last message from the messages
            messages = messages[:-1]
            # Append the tool result to the messages
            logger.info(f"Appending tool result to messages: {task.get('body', [{}])}")
            messages.append({
                "role": "user",
                "content": task.get('body', [{}])
            })
            return session_id, messages, "Continue", parent
        else:
            logger.info("No messages found in agent memory, starting a new conversation")
            return session_id, [], "Continue", parent
    logger.error(f"Unknown task type: {type}")
    return str(uuid.uuid4()), [], "Hello, how can you help?", parent

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
    session_id, history, prompt, parent = prepare(record)

    system_prompt = """
    You are a specialized content evaluator for Unicorn Rentals, a company that offers unicorns for rent that kids and grown-ups can play with.

    Your task is to evaluate social media posts for UniTok, our unicorn-themed social media platform, and ensure they adhere to our brand guidelines.

    Brand Guidelines for Unicorn Rentals:
    1. Content must be family-friendly and positive
    2. Posts should highlight the magical experience of spending time with unicorns
    3. When mentioning our new color selection feature, it should be accurate (colors: pink, blue, purple, green, yellow, and rainbow)
    4. Our brand voice is magical, playful, and family-friendly
    5. Posts should be between 50-200 characters for optimal engagement
    6. Emojis should be used sparingly but effectively
    7. Content should appeal to our target audience: families with children, fantasy enthusiasts, and event planners

    For each post you evaluate:
    1. Check if it adheres to ALL brand guidelines
    2. Provide a clear APPROVED or REJECTED decision
    3. If rejected, provide specific feedback on what needs to be improved
    4. If approved, provide a brief explanation of why it meets our guidelines

    Your evaluation should be thorough but concise.
    Once evaluation is complete, publish your evaluations.
    """
    # Create model
    model = BedrockModel(
        model_id="us.anthropic.claude-3-7-sonnet-20250219-v1:0",
        region_name="us-east-1"
    )

    # Create agent
    agent = Agent(
        system_prompt=system_prompt,
        model=model,
        tools=[publish_evaluation],
        messages=history,
    )
    
    result = agent(prompt, session_id=session_id, parent=parent)

    if result.state.get("stop_event_loop", False):
        logger.info("Agent needs to wait for tool result. Saving state and sleeping.")
    save_to_agent_memory(session_id, agent.messages, parent)

    logger.info(str(result))


