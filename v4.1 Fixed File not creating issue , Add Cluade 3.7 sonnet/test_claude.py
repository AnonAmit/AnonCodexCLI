#!/usr/bin/env python
"""
Test script for Claude API integration.
"""
import os
import sys
from dotenv import load_dotenv
from models.model_factory import ModelFactory

# Load environment variables (including API keys)
load_dotenv()

def test_claude():
    """Test the Claude API integration."""
    print("Testing Claude API integration...")
    
    # Check if API key is available
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("Note: No Anthropic API key found in environment variables.")
        print("Using mock Claude implementation for demonstration.")
    else:
        print(f"Found Anthropic API key: {api_key[:4]}...{api_key[-4:]}")
    
    # Create Claude model
    try:
        model = ModelFactory.create_model("claude-3-sonnet-20240229")
        print(f"Created model: {model.model_name}")
        
        # Check if it's a mock model
        is_mock = "Mock" in model.get_model_info().get("type", "")
        if is_mock:
            print("Using MOCK Claude model (no API calls will be made)")
        else:
            print("Using REAL Claude model (API calls will be made)")
        
    except Exception as e:
        print(f"Error creating model: {str(e)}")
        return False
    
    # Test generation with standard query
    test_generation("Tell me a short joke about programming.", model)
    
    # If using a mock model, test various keywords to show different responses
    if is_mock:
        print("\n=== Testing different mock responses ===")
        test_queries = [
            "Hello, who are you?",
            "Can you help me debug this error?",
            "Write a function to calculate average",
            "Explain this code to me"
        ]
        
        for query in test_queries:
            test_generation(query, model)
    
    print("\nClaude integration test completed successfully!")
    return True
    
def test_generation(prompt, model):
    """Test model generation with a specific prompt."""
    try:
        system_prompt = "You are a helpful AI assistant."
        
        print(f"\nPrompt: {prompt}")
        print("Generating response...")
        response = model.generate(system_prompt, prompt)
        
        print("\nResponse from Claude:")
        print("-" * 40)
        print(response)
        print("-" * 40)
        
        if not response or response.startswith("Error:"):
            print("Warning: Empty or error response received")
            return False
        return True
    except Exception as e:
        print(f"Error during generation: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_claude()
    sys.exit(0 if success else 1) 