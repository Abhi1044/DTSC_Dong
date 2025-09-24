"""
LLM Client for OpenAI Chat Completions
Handles the connection to the OpenAI API endpoint
"""

import openai
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

class LLMClient:
    def __init__(self):
        self.endpoint = os.getenv('OPENAI_ENDPOINT')
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.deployment_name = os.getenv('OPENAI_DEPLOYMENT')
        
        self.client = OpenAI(
            base_url=self.endpoint,
            api_key=self.api_key
        )
    
    def generate_completion(self, messages, max_tokens=2000, temperature=0.3):
        """
        Generate a completion using the OpenAI API
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            max_tokens: Maximum tokens in response
            temperature: Creativity level (0-1)
        
        Returns:
            String response from the model
        """
        try:
            response = self.client.chat.completions.create(
                model=self.deployment_name,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error calling LLM: {e}")
            return None

    def test_connection(self):
        """Test the LLM connection with a simple query"""
        test_messages = [
            {
                "role": "user",
                "content": "Say 'Connection successful!' if you can read this."
            }
        ]
        
        response = self.generate_completion(test_messages)
        return response

if __name__ == "__main__":
    # Test the client
    client = LLMClient()
    result = client.test_connection()
    print(f"Test result: {result}")