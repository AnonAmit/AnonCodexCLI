"""
Manual mode implementation.
"""
from typing import Dict, Any, Optional, List

from ui.components import (
    print_header, 
    print_info, 
    print_error, 
    print_success, 
    get_user_input,
    print_model_response,
    confirm_action,
    select_option,
    clear_screen
)
from ui.prompts import get_prompt_for_mode
from models.gemini import GeminiModel

class ManualMode:
    """Manual mode for AnonCodexCli."""
    
    def __init__(self, model=None, context: Optional[Dict[str, Any]] = None):
        """
        Initialize manual mode.
        
        Args:
            model: LLM model instance
            context: Additional context
        """
        self.model = model or GeminiModel()
        self.context = context or {}
        self.conversation_history = []
        self.mode_name = "manual"
        
    def start(self):
        """Start manual mode."""
        print_header("AnonCodexCli - Manual Mode")
        print_info("In manual mode, all actions require your confirmation.")
        print_info("Type your task below. Type 'exit' or 'quit' to exit.")
        print_info("")
        
        # Main interaction loop
        while True:
            # Get user input
            query = get_user_input("Enter your task")
            
            # Process special commands
            if query.lower() in ["exit", "quit"]:
                print_info("Exiting manual mode...")
                break
            elif query.lower() == "clear":
                clear_screen()
                continue
                
            # Process task with manual approval
            try:
                # First, get the suggested actions
                actions = self._get_suggested_actions(query)
                
                # Display suggested actions
                print_header("Suggested Actions", clear=False)
                print_model_response(actions)
                
                # Ask for confirmation
                if not confirm_action("Do you want to proceed with these actions?"):
                    print_info("Task execution canceled.")
                    continue
                
                # Execute actions one by one
                self._execute_actions(query, actions)
                
            except Exception as e:
                print_error(f"Error: {str(e)}")
    
    def _get_suggested_actions(self, query: str) -> str:
        """
        Get suggested actions for a query.
        
        Args:
            query: User query
            
        Returns:
            Suggested actions as text
        """
        planning_task = f"Suggest a list of specific actions to accomplish the following task. For each action, provide a clear description of what will be done:\n\n{query}"
        
        # Get prompt
        prompt = get_prompt_for_mode(self.mode_name, planning_task, self.context)
        
        # Generate suggested actions
        actions = self.model.generate(prompt["system"], prompt["user"])
        
        return actions
    
    def _execute_actions(self, query: str, actions: str):
        """
        Execute actions one by one with approval.
        
        Args:
            query: Original user query
            actions: Suggested actions as text
        """
        # Extract individual actions
        action_items = self._extract_actions(actions)
        
        # Execute each action
        for i, action in enumerate(action_items, 1):
            print_header(f"Action {i}/{len(action_items)}", clear=False)
            print_info(f"Action: {action}")
            
            # Ask for confirmation
            options = ["Approve and execute", "Skip action", "Modify action", "Cancel all remaining actions"]
            choice = select_option(options, "What would you like to do?")
            
            if choice == 0:  # Approve and execute
                # Execute the action
                execution_task = f"Execute the following action for task: {query}\n\nAction: {action}"
                execution_prompt = get_prompt_for_mode(self.mode_name, execution_task, self.context)
                
                # Generate execution result
                result = self.model.generate(execution_prompt["system"], execution_prompt["user"])
                
                # Display result
                print_model_response(result)
                
                # Update context with the execution result
                self.context.update({f"action_{i}_result": result})
                
            elif choice == 1:  # Skip action
                print_info(f"Skipping action: {action}")
                continue
                
            elif choice == 2:  # Modify action
                modified_action = get_user_input("Enter modified action", multiline=True)
                
                # Execute the modified action
                execution_task = f"Execute the following action for task: {query}\n\nAction: {modified_action}"
                execution_prompt = get_prompt_for_mode(self.mode_name, execution_task, self.context)
                
                # Generate execution result
                result = self.model.generate(execution_prompt["system"], execution_prompt["user"])
                
                # Display result
                print_model_response(result)
                
                # Update context with the execution result
                self.context.update({f"action_{i}_result": result})
                
            elif choice == 3:  # Cancel all remaining actions
                print_info("Cancelling remaining actions.")
                break
            
            # Pause between actions
            if i < len(action_items):
                input("\nPress Enter to continue to the next action...")
        
        # Summary after all actions
        print_header("Task Execution Complete", clear=False)
        
        # Generate summary
        summary_task = f"Provide a summary of the results for task: {query}"
        summary_prompt = get_prompt_for_mode(self.mode_name, summary_task, self.context)
        
        # Generate summary
        summary = self.model.generate(summary_prompt["system"], summary_prompt["user"])
        
        # Display summary
        print_model_response(summary)
    
    def _extract_actions(self, actions_text: str) -> List[str]:
        """
        Extract individual actions from actions text.
        
        Args:
            actions_text: Text containing suggested actions
            
        Returns:
            List of individual actions
        """
        actions = []
        
        # Try to extract numbered actions (e.g., "1. Action one")
        import re
        numbered_actions = re.findall(r'(?:\d+\.|\-)\s*(.*?)(?=\n\d+\.|\n\-|\Z)', actions_text, re.DOTALL)
        
        if numbered_actions:
            actions = [action.strip() for action in numbered_actions]
        else:
            # If no numbered actions found, split by new lines
            actions = [line.strip() for line in actions_text.split('\n') if line.strip()]
        
        return actions 