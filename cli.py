#!/usr/bin/env python3
"""
AnonCodexCli - A CLI-based AI coding assistant inspired by Cursor.
"""
import os
import sys
import argparse
from typing import Dict, Any, Optional

from rich.console import Console
from rich.prompt import Prompt

# Import core modules
import config
from config.settings import initialize as init_settings
from ui.components import print_header, print_info, print_error, print_mode_selection, select_option
from models.model_factory import ModelFactory
from modes import get_mode_class

console = Console()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="AnonCodexCli - A CLI-based AI coding assistant")
    
    parser.add_argument(
        "--mode", "-m",
        choices=["interactive", "autonomous", "manual"],
        default=config.DEFAULT_MODE,
        help="Operation mode (default: %(default)s)"
    )
    
    parser.add_argument(
        "--model", 
        default=config.DEFAULT_MODEL,
        help="LLM model to use (default: %(default)s)"
    )
    
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="Enable debug mode"
    )
    
    parser.add_argument(
        "--query", "-q",
        help="Query to process (if provided, runs in non-interactive mode and exits after completion)"
    )
    
    return parser.parse_args()

def select_mode() -> str:
    """
    Display mode selection UI and get user choice.
    
    Returns:
        Selected mode name
    """
    print_mode_selection()
    
    # Get user selection
    mode_options = ["Interactive", "Autonomous", "Manual"]
    choice = select_option(mode_options, "Select operation mode")
    
    # Map choice to mode name
    mode_map = {
        0: "interactive",
        1: "autonomous",
        2: "manual"
    }
    
    return mode_map.get(choice, "interactive")

def select_model() -> str:
    """
    Display model selection UI and get user choice.
    
    Returns:
        Selected model name
    """
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
    
    # Get user selection
    choice = select_option(model_options, "Select LLM model")
    
    # Return model name
    return model_map.get(choice, config.DEFAULT_MODEL)

def initialize_model(model_name: str):
    """
    Initialize the LLM model.
    
    Args:
        model_name: Name of the model to initialize
        
    Returns:
        Initialized model instance
    """
    try:
        return ModelFactory.create_model(model_name)
    except Exception as e:
        print_error(f"Error initializing model: {str(e)}")
        # Try to fallback to default model
        try:
            print_info(f"Falling back to default model: {config.DEFAULT_MODEL}")
            return ModelFactory.create_model(config.DEFAULT_MODEL)
        except Exception:
            print_error("Failed to initialize even the default model. Please check your API keys.")
            sys.exit(1)

def main():
    """Main entry point."""
    # Initialize settings
    init_settings()
    
    # Parse arguments
    args = parse_args()
    
    # Show welcome message
    print_header("AnonCodexCli - AI Coding Assistant")
    
    # Get operation mode
    mode_name = args.mode
    
    # If mode not specified in args, prompt user to select
    if not args.query:  # Only prompt for mode in interactive session
        mode_name = select_mode()
    
    # Get model name
    model_name = args.model
    
    # If running interactively and default model is specified, ask user to select
    if not args.query and model_name == config.DEFAULT_MODEL:
        model_name = select_model()
    
    # Initialize model
    model = initialize_model(model_name)
    
    # Get mode class
    ModeClass = get_mode_class(mode_name)
    
    # Initialize mode with context
    context = {
        "current_directory": os.getcwd(),
        "model_name": model_name,
        "debug": args.debug
    }
    
    mode = ModeClass(model=model, context=context)
    
    # Process query or start interactive session
    if args.query:
        result = mode.process_query(args.query)
        print(result)
    else:
        # Start mode
        try:
            mode.start()
        except KeyboardInterrupt:
            print_info("\nExiting AnonCodexCli. Goodbye!")
            sys.exit(0)

if __name__ == "__main__":
    main() 