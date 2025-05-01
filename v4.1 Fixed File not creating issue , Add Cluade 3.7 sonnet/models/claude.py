"""
Claude API integration for AnonCodexCli.
"""
import os
import json
import requests
from typing import Dict, Any, Optional, List

from config.settings import ANTHROPIC_API_KEY

class ClaudeModel:
    """Claude API wrapper for Anthropic's Claude models."""
    
    def __init__(self, model_name: str = "claude-3-opus-20240229"):
        """
        Initialize the Claude model.
        
        Args:
            model_name: The Claude model to use
        """
        self.api_key = self._get_api_key()
        self.model_name = model_name
        self.api_url = "https://api.anthropic.com/v1/messages"
        
        # Available Claude models
        self.available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
        
        # Validate model name
        if model_name not in self.available_models:
            print(f"Warning: {model_name} is not in the list of known Claude models. Using anyway.")
            
    def _get_api_key(self) -> str:
        """Get the API key from environment or config."""
        # Try environment variable
        api_key = os.environ.get("ANTHROPIC_API_KEY") or ANTHROPIC_API_KEY
            
        # Raise error if no API key found
        if not api_key:
            raise ValueError(
                "No Claude API key found. Please set the ANTHROPIC_API_KEY environment variable or add it to the config."
            )
            
        return api_key
        
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 4000) -> str:
        """
        Generate a response from Claude.
        
        Args:
            system_prompt: The system prompt to provide context
            user_prompt: The user query/prompt
            max_tokens: Maximum tokens in the response
            
        Returns:
            The generated response text
        """
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json"
        }
        
        payload = {
            "model": self.model_name,
            "system": system_prompt,
            "messages": [
                {"role": "user", "content": user_prompt}
            ],
            "max_tokens": max_tokens
        }
        
        try:
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            
            result = response.json()
            return result["content"][0]["text"]
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error communicating with Claude API: {str(e)}"
            
            if hasattr(e, "response") and e.response:
                try:
                    error_data = e.response.json()
                    error_msg = f"Claude API Error: {error_data.get('error', {}).get('message', str(e))}"
                except:
                    pass
                    
            print(error_msg)
            return f"Error: {error_msg}"
            
    def list_models(self) -> List[str]:
        """List available Claude models."""
        return self.available_models
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        return {
            "name": self.model_name,
            "provider": "Anthropic",
            "type": "API",
            "description": "Claude is a family of AI assistants created by Anthropic."
        } 