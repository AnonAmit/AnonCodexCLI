#!/usr/bin/env python3
"""
Test script for verifying LLM integrations.
"""
import os
import sys
import time
from typing import List, Dict, Any

from config.settings import initialize
from models.model_factory import ModelFactory
from ui.components import (
    print_header,
    print_info,
    print_error,
    print_success,
    print_model_response,
    select_option
)

# Initialize settings
initialize()

# Test prompts
TEST_PROMPTS = [
    "Write a simple Python function that calculates the Fibonacci sequence.",
    "Explain the difference between a list and a tuple in Python.",
    "What's the best way to handle errors in JavaScript?",
    "Write a SQL query to find the top 5 customers by purchase amount.",
    "Debug this code: ```python\ndef add_numbers(a, b):\n    return a - b  # Bug here\n```"
]

def test_model(model_name: str, prompts: List[str] = None):
    """
    Test a model with a set of prompts.
    
    Args:
        model_name: Name of the model to test
        prompts: List of prompts to test with (defaults to TEST_PROMPTS)
    """
    if prompts is None:
        prompts = TEST_PROMPTS
    
    print_header(f"Testing {model_name}")
    
    try:
        # Create the model
        print_info(f"Initializing {model_name}...")
        model = ModelFactory.create_model(model_name)
        print_success("Model initialized successfully")
        
        # Test each prompt
        for i, prompt in enumerate(prompts, 1):
            print_info(f"\nPrompt {i}/{len(prompts)}: {prompt[:50]}...")
            
            # Time the response
            start_time = time.time()
            response = model.generate(
                system_prompt="You are a helpful AI assistant specialized in programming.",
                user_prompt=prompt
            )
            elapsed_time = time.time() - start_time
            
            # Print the response
            print_info(f"Response time: {elapsed_time:.2f} seconds")
            print_model_response(response)
            
            # Pause between prompts
            if i < len(prompts):
                input("\nPress Enter for the next prompt...")
        
        print_success(f"All prompts tested successfully with {model_name}")
        
    except Exception as e:
        print_error(f"Error testing {model_name}: {str(e)}")
        return False
    
    return True

def main():
    """Main entry point."""
    print_header("AnonCodexCli Model Test")
    
    # Get available models
    available_models = ModelFactory.list_available_models()
    model_options = []
    model_map = {}
    
    # Format available models for display
    idx = 0
    for family, models in available_models.items():
        for model in models:
            model_options.append(f"{family.capitalize()}: {model}")
            model_map[idx] = model
            idx += 1
    
    # Add option to test all models
    model_options.append("Test all models")
    
    # Get user selection
    choice = select_option(model_options, "Select model to test")
    
    if choice < len(model_map):
        # Test a single model
        model_name = model_map[choice]
        test_model(model_name)
    else:
        # Test all models
        for model_name in model_map.values():
            success = test_model(model_name)
            if not success:
                print_info(f"Skipping remaining tests after failure with {model_name}")
                break
            print_info("\n" + "-" * 50 + "\n")

if __name__ == "__main__":
    main() 