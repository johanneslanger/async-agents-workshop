import logging
import os
import boto3
import json
from typing import Any
from botocore.exceptions import ClientError
from strands.types.tools import ToolResult, ToolUse

# Initialize logging and set paths
logger = logging.getLogger(__name__)
POST_GENERATOR_AGENT_SQS_URL = os.environ.get("POST_GENERATOR_AGENT_SQS_URL", None)
TOOL_SPEC = {
    "name": "publish_evaluation",
    "description": "Report back the evaluation results",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "evaluation": {
                    "type": "string",
                    "description": "Thorough and concise evaluation report with APPROVED or REJECTED remarks along with feedback on areas of improvment"
                }
            },
            "required": ["evaluation"]
        }
    }
}

def evaluator(tool: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool["toolUseId"]
    content = tool["input"]["evaluation"]
    request_state = kwargs.get("request_state", {})
    session_id = request_state.get('session_id', kwargs.get("session_id", None))
    parent = request_state.get('parent', kwargs.get("parent", None))
    logger.debug(f"Session ID: {session_id}")

    # Send an existing task to report to parent agent via SQS
    # Structure of an existing task
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
    message_body = {
        "session_id": session_id,
        "type": "existing",
        "toolName": "evaluator_agent",
        "body": {
            'toolResult': {
                'toolUseId': parent['tool_use_id'],
                'status': 'success',
                'content': [{'text': content}]
            }
        }
    }
        
    sqs = boto3.client('sqs')
    sqs.send_message(
        QueueUrl=POST_GENERATOR_AGENT_SQS_URL,
        MessageBody=json.dumps(message_body),
        MessageAttributes={
            'session_id': {
                'StringValue': session_id,
                'DataType': 'String'
            },
            'tool_use_id': {
                'StringValue': parent['tool_use_id'],
                'DataType': 'String'
            }
        }
    )

    # Set the stop flag, so that the agent can sleep and store it's state in memory.
    request_state["stop_event_loop"] = True

    # Return success page
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'text/html'},
        'body': "Reported evaluation results to the requester"
    }