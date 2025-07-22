import json
import requests
from bs4 import BeautifulSoup
import logging

# Configure logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Constants
MAX_CONTENT_SIZE_BYTES = 1 * 1024 * 1024  # 1 MB
REQUEST_TIMEOUT_SECONDS = 10
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def clean_html(html_content):
    """
    Parses HTML content, removes script/style tags, and returns clean text.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(['script', 'style']):
        script_or_style.decompose()
        
    # Get text, separated by spaces, and remove extra whitespace
    text = soup.get_text(separator=' ', strip=True)
    
    # Limit to first 2000 characters for brevity in agent response
    return text[:2000]

def lambda_handler(event, context):
    """
    Lambda handler that is invoked by the Bedrock Agent.
    """
    logger.info(f"Received event: {json.dumps(event)}")
    
    # Bedrock sends the API path and parameters in the event
    action_group = event['actionGroup']
    api_path = event['apiPath']
    
    # Extract the URL from the request body properties
    try:
        # The actual parameters are in a JSON string within the requestBody
        body = json.loads(event['requestBody']['content']['application/json']['body'])
        url_to_scrape = body.get('url')
        
        if not url_to_scrape:
            raise ValueError("URL parameter is missing.")
            
    except (KeyError, json.JSONDecodeError, ValueError) as e:
        logger.error(f"Error parsing input: {e}")
        return {
            'messageVersion': '1.0',
            'response': {
                'actionGroup': action_group,
                'apiPath': api_path,
                'httpMethod': event['httpMethod'],
                'httpStatusCode': 400,
                'responseBody': {
                    'application/json': {
                        'body': json.dumps({'error': 'Invalid request format or missing URL.'})
                    }
                }
            }
        }
    
    logger.info(f"Starting to scrape URL: {url_to_scrape}")
    
    try:
        # Fetch the webpage
        response = requests.get(
            url_to_scrape, 
            headers=HEADERS, 
            timeout=REQUEST_TIMEOUT_SECONDS, 
            allow_redirects=True, # Handles redirects automatically
            stream=True # Stream to control download size
        )
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # Check content type to avoid downloading binary files
        content_type = response.headers.get('content-type', '').lower()
        if 'text/html' not in content_type:
            raise ValueError(f"Content-Type is not text/html, but {content_type}")

        # Handle size limit
        content_length = int(response.headers.get('content-length', 0))
        if content_length > MAX_CONTENT_SIZE_BYTES:
             raise ValueError(f"Content size {content_length} exceeds limit of {MAX_CONTENT_SIZE_BYTES} bytes.")

        # Read content within the size limit
        html_content = response.content
        
        # Clean the HTML to get plain text
        plain_text_snippets = clean_html(html_content)
        
        # Successful response format for Bedrock Agent
        response_body = {
            'application/json': {
                'body': json.dumps({'snippets': plain_text_snippets})
            }
        }
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Request failed: {e}")
        response_body = {'application/json': {'body': json.dumps({'error': f"Failed to fetch URL: {str(e)}"})}}
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        response_body = {'application/json': {'body': json.dumps({'error': f"Error processing URL: {str(e)}"})}}


    action_response = {
        'messageVersion': '1.0',
        'response': {
            'actionGroup': action_group,
            'apiPath': api_path,
            'httpMethod': event['httpMethod'],
            'httpStatusCode': 200,
            'responseBody': response_body
        }
    }
    
    return action_response