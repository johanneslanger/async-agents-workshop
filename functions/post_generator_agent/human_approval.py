import logging
import os
import boto3
import json
from typing import Any
from botocore.exceptions import ClientError
from strands.types.tools import ToolResult, ToolUse

# Initialize logging and set paths
logger = logging.getLogger(__name__)
TOPIC_ARN = os.environ.get("TOPIC_ARN", None)
APPROVAL_API_ENDPOINT = os.environ.get("APPROVAL_API_ENDPOINT", None)

TOOL_SPEC = {
    "name": "human_approval",
    "description": "Request approval from a human for the content generated or critical decisions.",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "Content or decision that needs to be approved by the human."
                }
            },
            "required": ["content"]
        }
    }
}

def send_approval_email(content_to_approve, session_id, tool_use_id):
    """
    Sends an approval request email via SNS with approve/deny links
    
    Parameters:
    session_id (str): The id of the session currently running
    content_to_approve (str): The content that needs approval
    
    Returns:
    dict: Response from SNS publish or error information
    """
    try:
        assert session_id is not None, "Session ID is not specified"
        assert TOPIC_ARN is not None, "TOPIC_ARN is not specified"
        assert APPROVAL_API_ENDPOINT is not None, "APPROVAL_API_ENDPOINT is missing"
        # Create an SNS client
        sns_client = boto3.client('sns')
        
        # Create the approval and denial URLs
        approve_url = f"{APPROVAL_API_ENDPOINT}approve/{session_id}?toolUseId={tool_use_id}"
        deny_url = f"{APPROVAL_API_ENDPOINT}deny/{session_id}?toolUseId={tool_use_id}"
        
        # Plain text alternative for email clients that don't support HTML
        text_message = f"""
        Content Approval Request
        
        The following content has been generated and requires your approval:
        
        {content_to_approve}
        
        To approve: {approve_url}
        To deny: {deny_url}
        
        """
        
        # Create the message structure with both HTML and plain text versions
        message = {
            "default": text_message,
            "email": text_message,
            "email-json": json.dumps({
                "subject": "Content Approval Request",
                "body": {
                    "text": text_message
                }
            })
        }
        
        # Publish the message to the SNS topic
        response = sns_client.publish(
            TopicArn=TOPIC_ARN,
            Message=json.dumps(message),
            Subject="Content Approval Request",
            MessageStructure='json'
        )
        
        message = "An email has been sent successfully to request content approval"
        
        return {
            "success": True,
            "message_id": response['MessageId'],
            "message": message,
        }
        
    except ClientError as e:
        print(f"Error sending email: {e}")
        return {
            "success": False,
            "error": str(e)
        }


def human_approval(tool: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool["toolUseId"]
    content = tool["input"]["content"]
    request_state = kwargs.get("request_state", {})
    session_id = request_state.get('session_id', kwargs.get("session_id", None))

    logger.debug(f"Session ID: {session_id}")

    # Send out an SNS notification to request human feedback with content
    status = send_approval_email(content, session_id, tool_use_id)

    # Set the stop flag, so that the agent can sleep and store it's state in memory.
    request_state["stop_event_loop"] = True
    request_state["session_id"] = session_id

    return {
        "toolUseId": tool_use_id,
        "status": "success",
        "content": [{"text": status['message']}]
    }