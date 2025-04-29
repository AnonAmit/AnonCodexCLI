"""
Anthropic Claude API integration.
"""
import os
import json
from typing import Dict, Any, List, Optional

from config import ANTHROPIC_API_KEY

class ClaudeModel:
    """Claude model integration."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "claude-3-sonnet-20240229"):
        """
        Initialize the Claude model.
        
        Args:
            api_key: Anthropic API key (defaults to environment variable)
            model_name: Model name (e.g., "claude-3-opus", "claude-3-sonnet")
        """
        self.api_key = api_key or ANTHROPIC_API_KEY
        self.model_name = model_name
        
        # Configure the API
        if not self.api_key:
            raise ValueError("Anthropic API key is required")
        
        try:
            import anthropic
            self.client = anthropic.Anthropic(api_key=self.api_key)
        except ImportError:
            raise ImportError("Anthropic package not installed. Install it with 'pip install anthropic'")
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Claude client: {str(e)}")
    
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
            message = self.client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": user_prompt}
                ],
                temperature=temperature,
                max_tokens=4096
            )
            
            return message.content[0].text
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
            # Extract system prompt
            system_prompt = ""
            formatted_messages = []
            
            for message in messages:
                if message["role"] == "system":
                    system_prompt = message["content"]
                else:
                    # Format as Claude expects
                    formatted_messages.append({
                        "role": "user" if message["role"] == "user" else "assistant",
                        "content": message["content"]
                    })
            
            # Create Claude message
            message = self.client.messages.create(
                model=self.model_name,
                system=system_prompt,
                messages=formatted_messages,
                temperature=temperature,
                max_tokens=4096
            )
            
            return message.content[0].text
        except Exception as e:
            return f"Error in chat generation: {str(e)}" 