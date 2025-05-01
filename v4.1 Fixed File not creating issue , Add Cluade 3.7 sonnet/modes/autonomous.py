"""
Autonomous mode implementation.
"""
from typing import Dict, Any, Optional, List
import time
import re
import os

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
from utils.file_operations import write_file, is_safe_path

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
                
                # Extract and create files
                self._extract_and_create_files(result)
                
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
        
        # Try to extract numbered steps with various formats:
        # - "1. Step one"
        # - "Step 1: Do something"
        # - "- Step one"
        # - "1) Step one"
        patterns = [
            r'(?:\d+\.)\s*(.*?)(?=\n\d+\.|\Z)',  # Format: "1. Step"
            r'(?:Step\s+\d+:)\s*(.*?)(?=\n(?:Step\s+\d+:)|\Z)',  # Format: "Step 1: Do something"
            r'(?:\-)\s*(.*?)(?=\n\-|\Z)',  # Format: "- Step"
            r'(?:\d+\))\s*(.*?)(?=\n\d+\)|\Z)',  # Format: "1) Step"
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, plan, re.DOTALL)
            if matches:
                steps = [step.strip() for step in matches]
                break
        
        # If no structured steps found, try to find sections separated by blank lines
        if not steps:
            sections = re.split(r'\n\s*\n', plan)
            steps = [section.strip() for section in sections if section.strip()]
        
        # If still no steps or only one big step, split by newlines
        if not steps or (len(steps) == 1 and len(steps[0].split('\n')) > 3):
            steps = [line.strip() for line in plan.split('\n') if line.strip()]
            
            # Filter out short lines that are likely headers
            steps = [step for step in steps if len(step) > 10]
        
        return steps
    
    def _extract_and_create_files(self, result: str):
        """
        Extract file content from the result and create the actual files.
        
        Args:
            result: Result text containing file information
        """
        # Pattern to match file content in format: 1:13:filename.ext or ```1:13:filename.ext
        # This improved pattern handles a wider range of filenames and paths
        file_pattern = r'(?:```)?(\d+:\d+:(?:[^\n]+?))\s*\n(.*?)(?=\n(?:```)?(?:\d+:\d+:|```|$)|\Z)'
        
        # Match all file references and their content
        matches = re.findall(file_pattern, result, re.DOTALL)
        
        for file_ref, content in matches:
            # Extract the filename
            try:
                # Split by the last colon to get the filename
                parts = file_ref.strip().split(':')
                if len(parts) < 3:
                    print_error(f"Invalid file reference format: {file_ref}")
                    continue
                    
                # The filename is everything after the second colon
                filename = ':'.join(parts[2:])
                
                # Validate the file path
                is_safe, message = is_safe_path(filename)
                if not is_safe:
                    print_error(f"File path '{filename}' is not safe: {message}")
                    continue
                
                # Create the directory if needed
                directory = os.path.dirname(filename)
                if directory and not os.path.exists(directory):
                    # Validate the directory path
                    is_safe, message = is_safe_path(directory)
                    if not is_safe:
                        print_error(f"Directory path '{directory}' is not safe: {message}")
                        continue
                    
                    os.makedirs(directory, exist_ok=True)
                
                # Cleanup the content (remove leading/trailing whitespace)
                cleaned_content = content.strip()
                
                # Write the file
                write_status = write_file(filename, cleaned_content)
                
                # Log success or failure
                if write_status.startswith("Successfully"):
                    print_success(f"Created/updated file: {filename}")
                else:
                    print_error(f"Failed to write file {filename}: {write_status}")
            except Exception as e:
                print_error(f"Failed to create file from {file_ref}: {str(e)}") 