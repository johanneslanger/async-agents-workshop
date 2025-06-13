import json
import boto3
import os
from datetime import datetime
import logging

logger = logging.getLogger()

sqs = boto3.client('sqs')
queue_url = os.environ['SQS_QUEUE_URL']

def lambda_handler(event, context):
    try:
        # Parse the request path parameters
        session_id = event['pathParameters']['session_id']
        # Parse the request query parameters
        tool_use_id = event['queryStringParameters']['toolUseId']

        approval = 'approved' if 'approve' in event['resource'] else 'denied'

        logger.info(f"Processing {approval} for session_id: {session_id}")
        
        # Send wake-up message to SQS
        message_body = {
            'session_id': session_id,
            'type': 'existing',
            'toolName': 'human_approval',
            'body': [{
                'toolResult': {
                    'toolUseId': tool_use_id,
                    'status': 'success',
                    'content': [{'text': approval}]
                }
            }]
        }

        sqs.send_message(
            QueueUrl=queue_url,
            MessageBody=json.dumps(message_body),
            MessageAttributes={
                'session_id': {
                    'StringValue': session_id,
                    'DataType': 'String'
                },
                'action': {
                    'StringValue': 'approval_response',
                    'DataType': 'String'
                },
                'tool_use_id': {
                    'StringValue': tool_use_id,
                    'DataType': 'String'
                }
            }
        )

        # Return success page
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'text/html'},
            'body': "Successfully notified agent"
        }

    except Exception as e:
        logger.error(f"Error processing approval: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'text/html'},
            'body': f"Failed with error {e}"
        }