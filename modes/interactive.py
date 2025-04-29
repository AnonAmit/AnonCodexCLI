"""
Interactive mode implementation.
"""
from typing import Dict, Any, Optional, List

from ui.components import (
    print_header, 
    print_info, 
    print_error, 
    print_success, 
    get_user_input,
    print_model_response,
    display_help,
    clear_screen
)
from ui.prompts import get_prompt_for_mode
from models.gemini import GeminiModel

class InteractiveMode:
    """Interactive mode for AnonCodexCli."""
    
    def __init__(self, model=None, context: Optional[Dict[str, Any]] = None):
        """
        Initialize interactive mode.
        
        Args:
            model: LLM model instance
            context: Additional context
        """
        self.model = model or GeminiModel()
        self.context = context or {}
        self.conversation_history = []
        self.mode_name = "interactive"
        
    def start(self):
        """Start interactive mode."""
        print_header("AnonCodexCli - Interactive Mode")
        print_info("Type your query below. Type 'help' for available commands.")
        print_info("Type 'exit' or 'quit' to exit.")
        print_info("")
        
        # Main interaction loop
        while True:
            # Get user input
            query = get_user_input("> ")
            
            # Process special commands
            if query.lower() in ["exit", "quit"]:
                print_info("Exiting interactive mode...")
                break
            elif query.lower() == "help":
                display_help()
                continue
            elif query.lower() == "clear":
                clear_screen()
                continue
                
            # Process regular query
            try:
                # Get prompt
                prompt = get_prompt_for_mode(self.mode_name, query, self.context)
                
                # Update conversation history
                self.conversation_history.append({"role": "user", "content": prompt["user"]})
                
                # Generate response
                if len(self.conversation_history) == 1:
                    # First message, include system prompt
                    messages = [
                        {"role": "system", "content": prompt["system"]},
                        {"role": "user", "content": prompt["user"]}
                    ]
                else:
                    # Add to existing conversation
                    messages = [
                        {"role": "system", "content": prompt["system"]}
                    ] + self.conversation_history
                
                response = self.model.chat(messages)
                
                # Update conversation history
                self.conversation_history.append({"role": "assistant", "content": response})
                
                # Print response
                print_model_response(response)
                
            except Exception as e:
                print_error(f"Error: {str(e)}")
    
    def process_query(self, query: str) -> str:
        """
        Process a single query and return the response.
        
        Args:
            query: User query
            
        Returns:
            Model response
        """
        # Get prompt
        prompt = get_prompt_for_mode(self.mode_name, query, self.context)
        
        # Generate response
        response = self.model.generate(prompt["system"], prompt["user"])
        
        return response 