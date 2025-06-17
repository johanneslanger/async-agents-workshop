import os
import logging
import requests
from typing import Any
from botocore.exceptions import ClientError
from strands.types.tools import ToolResult, ToolUse

# Initialize logging and set paths
logger = logging.getLogger(__name__)
API_ENDPOINT = os.environ.get("PUBLISH_API_ENDPOINT", None)

TOOL_SPEC = {
    "name": "publish_post",
    "description": "Request approval from a human for the content generated or critical decisions.",
    "inputSchema": {
        "json": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The text content of the post."
                },
                "author": {
                    "type": "string",
                    "description": "The author of the post. Defaults to 'Unicorn Rentals'"
                },
                "unicorn_color":{
                    "type": "string",
                    "description": "The color of the unicorn. Choose from: pink, blue, purple, green, yellow, or rainbow. Defaults to 'rainbow'"
                },
                "image_url":{
                    "type": "string",
                    "description": "The image url of the unicorn. Defaults to None"
                }
            },
            "required": ["content"]
        }
    }
}

def publish_post(tool: ToolUse, **kwargs: Any) -> ToolResult:
    tool_use_id = tool["toolUseId"]
    request_state = kwargs.get("request_state", {})

    try:
        assert API_ENDPOINT is not None, "PUBLISH_API_ENDPOINT is not set, it is needed to post to UniTok"
        # Prepare the post data
        post_data = {
            "content": tool["input"]["content"],
            "author": tool["input"].get('author', "Unicorn Rentals"),
            "unicornColor": tool["input"].get('unicorn_color', "rainbow")
        }
        if tool["input"].get('image_url'):
            post_data["imageUrl"] = tool["input"].get('image_url')
        
        # Send the post to the API
        response = requests.post(API_ENDPOINT, json=post_data)
        
        # Check if the request was successful
        if response.status_code == 201:
            post_id = response.json().get("postId")
            return f"Post published successfully! Post ID: {post_id}"
        else:
            return f"Failed to publish post. Status code: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        return f"Error publishing post: {str(e)}"
        