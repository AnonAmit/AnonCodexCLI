"""
Google Gemini API integration.
"""
import os
import json
import google.generativeai as genai
from typing import Dict, Any, List, Optional

from config import GEMINI_API_KEY

class GeminiModel:
    """Google Gemini model integration."""
    
    def __init__(self, api_key: Optional[str] = None, model_name: str = "gemini-pro"):
        """
        Initialize the Gemini model.
        
        Args:
            api_key: Gemini API key (defaults to environment variable)
            model_name: Model name (e.g., "gemini-pro")
        """
        self.api_key = api_key or GEMINI_API_KEY
        self.model_name = model_name
        
        # Configure the API
        if not self.api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=self.api_key)
        
        # Generate configuration
        self.generation_config = {
            "temperature": 0.2,
            "top_p": 0.95,
            "top_k": 0,
            "max_output_tokens": 8192,
        }
        
        # Initialize the model
        try:
            self.model = genai.GenerativeModel(model_name=self.model_name)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize Gemini model: {str(e)}")
    
    def generate(self, system_prompt: str, user_prompt: str, 
                 temperature: Optional[float] = None) -> str:
        """
        Generate a response from the model.
        
        Args:
            system_prompt: System prompt
            user_prompt: User prompt
            temperature: Temperature for generation (overrides default)
            
        Returns:
            Model response
        """
        if temperature is not None:
            generation_config = self.generation_config.copy()
            generation_config["temperature"] = temperature
        else:
            generation_config = self.generation_config
        
        # Combine system and user prompts for Gemini
        combined_prompt = f"{system_prompt}\n\n{user_prompt}"
        
        try:
            response = self.model.generate_content(
                combined_prompt,
                generation_config=generation_config
            )
            
            return response.text
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def chat(self, messages: List[Dict[str, str]], 
             temperature: Optional[float] = None) -> str:
        """
        Generate a chat response from the model.
        
        Args:
            messages: List of message dictionaries with "role" and "content"
            temperature: Temperature for generation (overrides default)
            
        Returns:
            Model response
        """
        # Extract system prompt and user messages
        system_prompt = ""
        user_messages = []
        
        for message in messages:
            if message["role"] == "system":
                system_prompt = message["content"]
            else:
                user_messages.append(message)
        
        # Format user messages as a conversation
        conversation = []
        for message in user_messages:
            if message["role"] == "user":
                conversation.append({"role": "user", "parts": [message["content"]]})
            elif message["role"] == "assistant":
                conversation.append({"role": "model", "parts": [message["content"]]})
        
        if temperature is not None:
            generation_config = self.generation_config.copy()
            generation_config["temperature"] = temperature
        else:
            generation_config = self.generation_config
        
        try:
            # Initialize chat session with system prompt as initial context
            chat = self.model.start_chat(system_instruction=system_prompt)
            
            # Add all messages except the last user message
            for message in conversation[:-1]:
                if message["role"] == "user":
                    chat.send_message(message["parts"][0])
            
            # Generate response to the last user message
            if conversation and conversation[-1]["role"] == "user":
                response = chat.send_message(
                    conversation[-1]["parts"][0],
                    generation_config=generation_config
                )
                return response.text
            else:
                return "No user message to respond to."
        except Exception as e:
            return f"Error in chat generation: {str(e)}" 