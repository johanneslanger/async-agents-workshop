import logging
import os
import boto3
import json
from typing import Any
from botocore.exceptions import ClientError
from strands.types.tools import ToolResult, ToolUse

# Initialize logging and set paths
logger = logging.getLogger(__name__)
EVALUATOR_AGENT_SQS_URL = os.environ.get("EVALUATOR_AGENT_SQS_URL", None)

TOOL_SPEC = {
    "name": "evaluator_agent",
    "description": "Request evaluation of a social media post for adherence to Unicorn Rentals brand guidelines.",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content of the post to evaluate."
                }
            },
            "required": ["content"]
        }
    }
}

def evaluator_agent(tool: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool["toolUseId"]
    content = tool["input"]["content"]
    request_state = kwargs.get("request_state", {})
    session_id = request_state.get('session_id', kwargs.get("session_id", None))
    parent = request_state.get('parent', kwargs.get("parent", None))
    logger.debug(f"Session ID: {session_id}")

    # Send a new task to the evaluator agent via SQS
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
    message_body = {
        "type": "new",
        "body": {
            "task": content
        }
    }
    if parent:
        message_body['parent'] = parent
        message_body['parent']['tool_use_id'] = tool_use_id
        
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=EVALUATOR_AGENT_SQS_URL,
        MessageBody=json.dumps(message_body),
        MessageAttributes={
            'session_id': {
                'StringValue': session_id,
                'DataType': 'String'
            },
            'tool_use_id': {
                'StringValue': tool_use_id,
                'DataType': 'String'
            }
        }
    )

    # Set the stop flag, so that the agent can sleep and store it's state in memory.
    request_state["stop_event_loop"] = True
    request_state["session_id"] = session_id
    
    # Return success page
    return {
        "toolUseId": tool_use_id,
        "status": "success",
        "content": [{"text": "Requested evaluation from evaluator agent and waiting for response"}]
    }