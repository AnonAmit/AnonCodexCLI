"""
MockClaude model implementation for when you don't have an API key.
This provides pre-defined responses to common questions for demo purposes.
"""
import time
import random
from typing import Dict, Any, List

class MockClaudeModel:
    """
    Mock Claude API that returns pre-defined responses.
    Use this for demonstrations when you don't have an actual API key.
    """
    
    def __init__(self, model_name: str = "claude-3-sonnet-20240229"):
        """
        Initialize the mock Claude model.
        
        Args:
            model_name: The Claude model to simulate
        """
        self.model_name = model_name
        
        # Available models to simulate
        self.available_models = [
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
            "claude-2.1",
            "claude-2.0",
            "claude-instant-1.2"
        ]
        
        # Pre-defined responses for common questions
        self.responses = {
            "hello": "Hello! I'm a mock Claude model. I'm here to help with coding tasks.",
            "help": "I can help by providing pre-defined responses for common questions. This is a mock implementation for demonstration purposes.",
            "joke": "Why do programmers prefer dark mode? Because light attracts bugs!",
            "code": "```python\ndef hello_world():\n    print('Hello, world!')\n```",
            "function": "```python\ndef calculate_average(numbers):\n    if not numbers:\n        return 0\n    return sum(numbers) / len(numbers)\n```",
            "error": "It looks like you're encountering an error. Try checking your syntax, imports, or variable definitions.",
            "debug": "Here are some debugging tips:\n1. Add print statements\n2. Use a debugger\n3. Check variable types\n4. Isolate the issue",
            "explain": "This code creates a function that takes a list of input values, processes them, and returns the transformed result."
        }
            
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 4000) -> str:
        """
        Generate a mock response based on the prompt.
        
        Args:
            system_prompt: Ignored in mock implementation
            user_prompt: Used to select a response
            max_tokens: Ignored in mock implementation
            
        Returns:
            A pre-defined response
        """
        # Simulate processing time
        print("Generating response...")
        time.sleep(1.5)
        
        # Convert prompt to lowercase for matching
        lower_prompt = user_prompt.lower()
        
        # Look for keywords to determine which response to send
        for keyword, response in self.responses.items():
            if keyword in lower_prompt:
                return response
                
        # If we detect code in the prompt, provide coding assistance
        if "code" in lower_prompt or "function" in lower_prompt or "class" in lower_prompt:
            return self.responses.get("code")
            
        # If we detect a question about an error, provide debugging help
        if "error" in lower_prompt or "bug" in lower_prompt or "fix" in lower_prompt:
            return self.responses.get("error")
            
        # Generate generic response for other queries
        generic_responses = [
            "I understand you're asking about that. Here's a sample approach you could take...",
            "That's an interesting question. Let me provide a simple example...",
            "I can help with that. Here's a basic implementation to get you started...",
            "Great question! Let me walk you through how this works..."
        ]
        
        return random.choice(generic_responses)
            
    def list_models(self) -> List[str]:
        """List available mock Claude models."""
        return self.available_models
        
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current mock model."""
        return {
            "name": f"{self.model_name} (Mock)",
            "provider": "Mock Anthropic",
            "type": "Mock API",
            "description": "This is a mock Claude model for demonstration purposes only."
        } 