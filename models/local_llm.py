"""
Local LLM support for Ollama and LM Studio.
"""
import os
import json
import requests
from typing import Dict, Any, List, Optional, Union

from config import OLLAMA_BASE_URL, LM_STUDIO_BASE_URL

class OllamaModel:
    """Ollama model integration."""
    
    def __init__(self, base_url: Optional[str] = None, model_name: str = "llama3"):
        """
        Initialize the Ollama model.
        
        Args:
            base_url: Ollama API base URL (defaults to environment variable)
            model_name: Model name (e.g., "llama3", "mistral", "mixtral")
        """
        self.base_url = base_url or OLLAMA_BASE_URL
        self.model_name = model_name
        
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/api/version")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to Ollama API: {response.text}")
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to Ollama API: {str(e)}")
    
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
            # Combine prompts for Ollama format
            combined_prompt = f"{system_prompt}\n\n{user_prompt}"
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "model": self.model_name,
                    "prompt": combined_prompt,
                    "temperature": temperature,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                return response.json().get("response", "")
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: float = 0.2) -> str:
        """
        Generate a chat response using Ollama's chat endpoint.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Temperature for generation
            
        Returns:
            Model response
        """
        try:
            # Format messages for Ollama
            formatted_messages = []
            
            for message in messages:
                role = message["role"]
                # Map 'system' role to 'system', everything else to 'user' or 'assistant'
                if role == "system":
                    role = "system"
                elif role == "user":
                    role = "user"
                else:
                    role = "assistant"
                
                formatted_messages.append({
                    "role": role,
                    "content": message["content"]
                })
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/chat",
                json={
                    "model": self.model_name,
                    "messages": formatted_messages,
                    "temperature": temperature,
                    "stream": False
                }
            )
            
            if response.status_code == 200:
                return response.json().get("message", {}).get("content", "")
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Error in chat generation: {str(e)}"


class LMStudioModel:
    """LM Studio model integration."""
    
    def __init__(self, base_url: Optional[str] = None, model_name: str = "custom"):
        """
        Initialize the LM Studio model.
        
        Args:
            base_url: LM Studio API base URL (defaults to environment variable)
            model_name: Model name (not used in API calls but stored for reference)
        """
        self.base_url = base_url or LM_STUDIO_BASE_URL
        self.model_name = model_name
        
        # Test connection
        try:
            response = requests.get(f"{self.base_url}/v1/models")
            if response.status_code != 200:
                raise ConnectionError(f"Failed to connect to LM Studio API: {response.text}")
        except requests.RequestException as e:
            raise ConnectionError(f"Failed to connect to LM Studio API: {str(e)}")
    
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
            # LM Studio uses OpenAI-compatible API
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": 4096
                }
            )
            
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: float = 0.2) -> str:
        """
        Generate a chat response using LM Studio's OpenAI-compatible endpoint.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Temperature for generation
            
        Returns:
            Model response
        """
        try:
            # Format messages for OpenAI format
            formatted_messages = []
            
            for message in messages:
                formatted_messages.append({
                    "role": message["role"],
                    "content": message["content"]
                })
            
            # Make API request
            response = requests.post(
                f"{self.base_url}/v1/chat/completions",
                json={
                    "messages": formatted_messages,
                    "temperature": temperature,
                    "max_tokens": 4096
                }
            )
            
            if response.status_code == 200:
                return response.json().get("choices", [{}])[0].get("message", {}).get("content", "")
            else:
                return f"Error: {response.text}"
        except Exception as e:
            return f"Error in chat generation: {str(e)}" 