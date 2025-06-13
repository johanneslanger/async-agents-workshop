import json
import os
import boto3
import decimal
from boto3.dynamodb.conditions import Key

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
        
        # Query posts by timestamp (most recent first)
        response = table.query(
            IndexName='TimestampIndex',
            KeyConditionExpression=Key('dummy').eq('POST'),
            ScanIndexForward=False,  # Sort in descending order (newest first)
            Limit=50  # Limit to 50 posts
        )
        
        # Return the posts
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps(response.get('Items', []), cls=DecimalEncoder)
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
