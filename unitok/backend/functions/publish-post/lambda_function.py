import json
import os
import uuid
import boto3
import decimal
from datetime import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')

# Helper class to convert a DynamoDB item to JSON
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            if o % 1 > 0:
                return float(o)
            else:
                return int(o)
        return super(DecimalEncoder, self).default(o)

def lambda_handler(event, context):
    try:
        print(f"Event: {json.dumps(event)}")
        
        # Get the table name from environment variables
        table_name = os.environ.get('POSTS_TABLE')
        table = dynamodb.Table(table_name)
        
        # Parse the request body
        if 'body' not in event:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Missing request body'}, cls=DecimalEncoder)
            }
            
        request_body = json.loads(event['body'])
        
        # Validate required fields
        if 'content' not in request_body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Content is required'}, cls=DecimalEncoder)
            }
        
        # Create a new post
        timestamp = int(datetime.now().timestamp() * 1000)  # Current time in milliseconds
        post_id = str(uuid.uuid4())
        
        post = {
            'postId': post_id,
            'content': request_body['content'],
            'author': request_body.get('author', 'Anonymous Unicorn'),
            'imageUrl': request_body.get('imageUrl'),
            'unicornColor': request_body.get('unicornColor', 'rainbow'),
            'timestamp': timestamp,
            'likes': 0,
            'dummy': 'POST'  # For GSI partitioning
        }
        
        # Save the post to DynamoDB
        table.put_item(Item=post)
        
        # Return the created post
        return {
            'statusCode': 201,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(post, cls=DecimalEncoder)
        }
        
    except Exception as e:
        print(f"Error: {str(e)}")
        
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal server error'}, cls=DecimalEncoder)
        }
