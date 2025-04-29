"""
Autonomous mode implementation.
"""
from typing import Dict, Any, Optional, List
import time

from ui.components import (
    print_header, 
    print_info, 
    print_error, 
    print_success, 
    get_user_input,
    print_model_response,
    print_progress,
    confirm_action,
    select_option,
    clear_screen
)
from ui.prompts import get_prompt_for_mode
from models.gemini import GeminiModel

class AutonomousMode:
    """Autonomous mode for AnonCodexCli."""
    
    def __init__(self, model=None, context: Optional[Dict[str, Any]] = None):
        """
        Initialize autonomous mode.
        
        Args:
            model: LLM model instance
            context: Additional context
        """
        self.model = model or GeminiModel()
        self.context = context or {}
        self.mode_name = "autonomous"
        self.show_code = True
        
    def start(self):
        """Start autonomous mode."""
        print_header("AnonCodexCli - Autonomous Mode")
        print_info("In autonomous mode, the assistant will plan and execute tasks.")
        print_info("Type your task below. Type 'exit' or 'quit' to exit.")
        
        # Ask if the user wants to see code in the terminal
        self.show_code = confirm_action("Show code in terminal? (No will only show progress)")
        print_info("")
        
        # Main interaction loop
        while True:
            # Get task description
            task = get_user_input("Enter your task")
            
            # Process special commands
            if task.lower() in ["exit", "quit"]:
                print_info("Exiting autonomous mode...")
                break
            elif task.lower() == "clear":
                clear_screen()
                continue
                
            # Process task
            try:
                self._execute_task(task)
            except Exception as e:
                print_error(f"Error executing task: {str(e)}")
    
    def _execute_task(self, task: str):
        """
        Execute a task autonomously.
        
        Args:
            task: Task description
        """
        # Step 1: Plan the task
        print_info("Planning task execution...")
        
        # Create planning prompt
        planning_task = f"Plan how to execute the following task: {task}\n\nCreate a step-by-step plan with numbered steps."
        planning_prompt = get_prompt_for_mode(self.mode_name, planning_task, self.context)
        
        # Generate plan
        plan = self.model.generate(planning_prompt["system"], planning_prompt["user"])
        
        # Extract steps from the plan
        steps = self._extract_steps(plan)
        
        # Display the plan
        print_header("Execution Plan", clear=False)
        print_model_response(plan)
        
        # Ask for confirmation
        if not confirm_action("Proceed with this plan?"):
            print_info("Task execution canceled.")
            return
        
        # Execute the plan step by step
        print_header("Executing Plan", clear=False)
        
        # Create progress bar
        with print_progress("Executing plan", len(steps)) as progress:
            task_id = progress.add_task("Executing plan", total=len(steps))
            
            for i, step in enumerate(steps, 1):
                # Update progress description
                progress.update(task_id, description=f"Step {i}/{len(steps)}: {step[:50]}...")
                
                # Create step prompt
                step_task = f"Execute step {i} of the plan: {step}\n\nTask: {task}"
                step_prompt = get_prompt_for_mode(self.mode_name, step_task, self.context)
                
                # Execute step
                result = self.model.generate(step_prompt["system"], step_prompt["user"])
                
                # Display result if show_code is True
                if self.show_code:
                    print_info(f"\nStep {i}/{len(steps)}:")
                    print_model_response(result)
                
                # Update progress
                progress.update(task_id, advance=1)
                
                # Small delay to show progress
                time.sleep(0.5)
        
        # Final summary
        print_header("Task Execution Complete", clear=False)
        
        # Create summary prompt
        summary_task = f"Provide a summary of the results for task: {task}"
        summary_prompt = get_prompt_for_mode(self.mode_name, summary_task, self.context)
        
        # Generate summary
        summary = self.model.generate(summary_prompt["system"], summary_prompt["user"])
        
        # Display summary
        print_model_response(summary)
    
    def _extract_steps(self, plan: str) -> List[str]:
        """
        Extract steps from the plan.
        
        Args:
            plan: Plan text
            
        Returns:
            List of steps
        """
        steps = []
        
        # Try to extract numbered steps (e.g., "1. Step one")
        import re
        numbered_steps = re.findall(r'(?:\d+\.|\-)\s*(.*?)(?=\n\d+\.|\n\-|\Z)', plan, re.DOTALL)
        
        if numbered_steps:
            steps = [step.strip() for step in numbered_steps]
        else:
            # If no numbered steps found, split by new lines
            steps = [line.strip() for line in plan.split('\n') if line.strip()]
        
        return steps 