import json
import boto3
import string
import random
import re
from urllib.parse import urlparse
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('ShortUrls')

def lambda_handler(event, context):
    """
    Handles:
    - POST requests to create short URLs
    - GET requests to redirect to original URLs
    """
    
    try:
        # Extract HTTP method and path from the event
        http_method = event.get('requestContext', {}).get('http', {}).get('method', '')
        raw_path = event.get('rawPath', '')
        
        if http_method == 'OPTIONS':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'GET,POST,OPTIONS'
                }
            }
        
        # Handle POST requests for URL shortening
        if http_method == 'POST':
            return handle_shorten_url(event)
        
        # Handle GET requests for URL redirection
        elif http_method == 'GET' and raw_path != '/':
            return handle_redirect(event)
        
        # Handle root path GET requests
        elif http_method == 'GET' and raw_path == '/':
            return {
                'statusCode': 200,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({
                    'message': 'URL Shortener API is running',
                    'endpoints': {
                        'POST /': 'Shorten a URL',
                        'GET /{short_id}': 'Redirect to original URL'
                    }
                })
            }
        
        else:
            return {
                'statusCode': 405,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Method not allowed'})
            }
            
    except Exception as e:
        print(f"Unexpected error in lambda_handler: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Internal server error'})
        }

def handle_shorten_url(event):
    """
    Handle POST requests to create a short URL.
    """
    
    try:
        body = event.get('body', '')
        if not body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Request body is required'})
            }
        
        if isinstance(body, str):
            try:
                request_data = json.loads(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'Invalid JSON in request body'})
                }
        else:
            request_data = body
        
        original_url = request_data.get('url', '').strip()
        if not original_url:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'URL is required'})
            }
    
        short_id = generate_short_id()
        
        max_attempts = 5
        for attempt in range(max_attempts):
            try:
                # Try to store the URL mapping
                table.put_item(
                    Item={
                        'id': short_id,
                        'url': original_url
                    },
                    ConditionExpression='attribute_not_exists(id)'  # Ensure uniqueness
                )
                break 
                
            except ClientError as e:
                if e.response['Error']['Code'] == 'ConditionalCheckFailedException':
                    short_id = generate_short_id()
                    if attempt == max_attempts - 1:
                        raise Exception("Failed to generate unique short ID after multiple attempts")
                else:
                    raise e
                
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({
                'short_id': short_id,
                'original_url': original_url,
                'message': 'URL shortened successfully'
            })
        }
        
    except ClientError as e:
        print(f"DynamoDB error in handle_shorten_url: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Database error occurred'})
        }
    
    except Exception as e:
        print(f"Error in handle_shorten_url: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Failed to shorten URL'})
        }

def handle_redirect(event):
    """
    Handle GET requests to redirect to the original URL.
    """
    
    try:
        raw_path = event.get('rawPath', '')
        short_id = raw_path.lstrip('/')  # Remove leading slash
        
        if not short_id:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Short ID is required'})
            }
        
        print(f"Looking up short ID: {short_id}")
        
        try:
            response = table.get_item(Key={'id': short_id})
            
            if 'Item' not in response:
                return {
                    'statusCode': 404,
                    'headers': {
                        'Access-Control-Allow-Origin': '*',
                        'Content-Type': 'application/json'
                    },
                    'body': json.dumps({'error': 'Short URL not found'})
                }
            
            original_url = response['Item']['url']
            print(f"Redirecting {short_id} -> {original_url}")
            
            return {
                'statusCode': 302,
                'headers': {
                    'Location': original_url
                }
            }
            
        except ClientError as e:
            print(f"DynamoDB error in handle_redirect: {str(e)}")
            return {
                'statusCode': 500,
                'headers': {
                    'Access-Control-Allow-Origin': '*',
                    'Content-Type': 'application/json'
                },
                'body': json.dumps({'error': 'Database error occurred'})
            }
    
    except Exception as e:
        print(f"Error in handle_redirect: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Content-Type': 'application/json'
            },
            'body': json.dumps({'error': 'Redirect failed'})
        }

def generate_short_id(length=6):
    """
    Generate a random short ID using alphanumeric characters.
    """
    characters = string.ascii_letters + string.digits
    safe_characters = ''.join(c for c in characters if c not in '0OlI')
    return ''.join(random.choice(safe_characters) for _ in range(length))