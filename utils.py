"""
Utility functions for the handson.ai application.
"""

from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()


def get_openrouter_client():
    """
    Returns a configured OpenAI client for OpenRouter API.
    
    Returns:
        OpenAI: Configured client with OpenRouter base URL and API key
        
    Raises:
        ValueError: If OPENROUTER_API_KEY is not found in environment variables
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    
    if not api_key:
        raise ValueError("OPENROUTER_API_KEY not found in environment variables")
    
    return OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=api_key,
    )
