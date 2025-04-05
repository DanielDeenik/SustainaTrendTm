#!/usr/bin/env python3
"""
Test OpenAI API key configuration
"""
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.error("OpenAI library not installed")
    exit(1)

def check_openai_key():
    """Check if OpenAI API key is valid"""
    # Get API key from environment
    api_key = os.environ.get("OPENAI_API_KEY")
    
    if not api_key:
        logger.error("OPENAI_API_KEY environment variable not set")
        return False
    
    # Log first and last few characters of the key (for debugging without exposing the full key)
    key_preview = f"{api_key[:5]}...{api_key[-4:]}" if len(api_key) > 10 else "too short"
    logger.info(f"API Key format: {key_preview}, Length: {len(api_key)}")
    
    try:
        # Create client with explicit API key
        client = OpenAI(api_key=api_key)
        
        # Make a simple completions request
        logger.info("Testing OpenAI API with a simple completions request...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ],
            max_tokens=10
        )
        
        # Check if we got a valid response
        if response and response.choices and len(response.choices) > 0:
            logger.info(f"API test successful! Response: {response.choices[0].message.content}")
            return True
        else:
            logger.error(f"API responded but with unexpected format: {response}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing OpenAI API: {str(e)}")
        return False

if __name__ == "__main__":
    if check_openai_key():
        print("✅ OpenAI API key is valid and working correctly!")
    else:
        print("❌ OpenAI API key validation failed. Check logs for details.")