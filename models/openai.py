"""
OpenAI API integration.
"""
import os
import json
from typing import Dict, Any, List, Optional

from config import OPENAI_API_KEY

class OpenAIModel:
    """OpenAI model integration."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gpt-3.5-turbo"):
        """
        Initialize the OpenAI model.
        
        Args:
            api_key: OpenAI API key (defaults to environment variable)
            model_name: Model name (e.g., "gpt-3.5-turbo", "gpt-4")
        """
        self.api_key = api_key or OPENAI_API_KEY
        self.model_name = model_name
        
        # Configure the API
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        try:
            import openai
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        except ImportError:
            raise ImportError("OpenAI package not installed. Install it with 'pip install openai'")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize OpenAI client: {str(e)}")
    
    def generate(self, system_prompt: str, user_prompt: str, 
                 temperature: float = 0.2) -> str:
        """
        Generate a response from the model.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature for generation
            
        Returns:
            Model response
        """
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=temperature,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: float = 0.2) -> str:
        """
        Generate a chat response from the model.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Temperature for generation
            
        Returns:
            Model response
        """
        try:
            # Format messages for OpenAI API
            formatted_messages = []
            
            for message in messages:
                formatted_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=4096
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error in chat generation: {str(e)}" 