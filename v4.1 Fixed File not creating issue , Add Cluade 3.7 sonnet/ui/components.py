"""
UI components module for terminal-based UI.
"""
import os
import platform
import sys
from typing import List, Optional, Any, Dict, Tuple
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.prompt import Prompt, Confirm
from rich.table import Table
from rich.markdown import Markdown
from rich import box

# Create console instance
console = Console()

# Colors
COLOR_PRIMARY = "cyan"
COLOR_SECONDARY = "blue"
COLOR_SUCCESS = "green"
COLOR_ERROR = "red"
COLOR_WARNING = "yellow"
COLOR_INFO = "white"
COLOR_CODE = "bright_black"

def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def print_header(text: str, clear: bool = True):
    """
    Print a header.
    
    Args:
        text: Header text
        clear: Whether to clear the screen first
    """
    if clear:
        clear_screen()
    
    console.print()
    console.print(Panel(
        f"[bold {COLOR_PRIMARY}]{text}[/]",
        border_style=COLOR_PRIMARY,
        expand=False
    ))
    console.print()

def print_mode_selection():
    """Print mode selection options."""
    console.print("[bold]Select Operation Mode:[/]")
    console.print()
    
    table = Table(box=box.ROUNDED, expand=False, show_header=False, border_style=COLOR_SECONDARY)
    table.add_column("Number", style=f"bold {COLOR_PRIMARY}")
    table.add_column("Mode", style="white")
    table.add_column("Description")
    
    table.add_row("1", "Interactive", "Ask questions and get responses")
    table.add_row("2", "Autonomous", "Let the AI plan and execute tasks")
    table.add_row("3", "Manual", "Control each step of the process")
    
    console.print(table)
    console.print()

def print_success(message: str):
    """
    Print a success message.
    
    Args:
        message: Success message
    """
    console.print(f"[bold {COLOR_SUCCESS}]✓ {message}[/]")

def print_error(message: str):
    """
    Print an error message.
    
    Args:
        message: Error message
    """
    console.print(f"[bold {COLOR_ERROR}]✗ {message}[/]")

def print_info(message: str):
    """
    Print an informational message.
    
    Args:
        message: Information message
    """
    console.print(f"[{COLOR_INFO}]{message}[/]")

def print_code(code: str, language: str = "python"):
    """
    Print formatted code.
    
    Args:
        code: Code to print
        language: Programming language for syntax highlighting
    """
    syntax = Syntax(code, language, theme="monokai", line_numbers=True, word_wrap=True)
    console.print(Panel(syntax, border_style=COLOR_CODE, expand=False))

def confirm_action(message: str) -> bool:
    """
    Ask for confirmation.
    
    Args:
        message: Confirmation message
        
    Returns:
        True if confirmed, False otherwise
    """
    return Confirm.ask(f"[bold {COLOR_WARNING}]{message}[/]")

def select_option(options: List[str], prompt: str = "Select an option") -> int:
    """
    Ask user to select an option.
    
    Args:
        options: List of options
        prompt: Prompt message
        
    Returns:
        Selected option index (0-based)
    """
    console.print(f"[bold]{prompt}:[/]")
    
    for i, option in enumerate(options, 1):
        console.print(f"  [bold {COLOR_PRIMARY}]{i}.[/] {option}")
    
    console.print()
    choice = Prompt.ask(
        "Enter number",
        choices=[str(i) for i in range(1, len(options) + 1)],
        default="1"
    )
    
    return int(choice) - 1

def get_user_input(prompt: str = "Enter your query", multiline: bool = False) -> str:
    """
    Get input from the user.
    
    Args:
        prompt: Input prompt
        multiline: Whether to allow multiline input
        
    Returns:
        User input
    """
    if multiline:
        console.print(f"[bold]{prompt}:[/] (Type 'END' on a new line to finish)")
        lines = []
        
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)
        
        return "\n".join(lines)
    else:
        return Prompt.ask(f"[bold]{prompt}[/]")

def print_progress(message: str, total_steps: int = 100):
    """
    Create and return a progress bar.
    
    Args:
        message: Progress message
        total_steps: Total number of steps
        
    Returns:
        Progress context manager
    """
    return Progress(
        SpinnerColumn(),
        TextColumn("[bold blue]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TimeElapsedColumn(),
        console=console
    )

def print_markdown(markdown_text: str):
    """
    Print markdown-formatted text.
    
    Args:
        markdown_text: Markdown text
    """
    md = Markdown(markdown_text)
    console.print(md)

def print_model_response(response: str):
    """
    Print a model response with appropriate formatting.
    
    Args:
        response: Model response text
    """
    # Check if the response contains code blocks
    if "```" in response:
        # Split by code blocks
        parts = response.split("```")
        
        for i, part in enumerate(parts):
            if i % 2 == 0:  # Text part
                if part.strip():
                    print_markdown(part)
            else:  # Code part
                # Handle language specification
                if "\n" in part:
                    lang, code = part.split("\n", 1)
                    lang = lang.strip()
                    if not lang:
                        lang = "text"
                else:
                    lang = "text"
                    code = part
                
                print_code(code.strip(), lang)
    else:
        # Just print as markdown
        print_markdown(response)

def display_help():
    """Display help information."""
    console.print(Panel(
        "[bold]AnonCodexCli Help[/]\n\n"
        "Available commands:\n"
        "- [bold]help[/]: Show this help message\n"
        "- [bold]clear[/]: Clear the screen\n"
        "- [bold]exit[/] or [bold]quit[/]: Exit the application\n"
        "- [bold]mode[/]: Change operation mode\n"
        "- [bold]model[/]: Change LLM model\n\n"
        "In interactive mode, just type your query and press Enter.\n"
        "In autonomous mode, type a task description and the AI will plan and execute it.\n"
        "In manual mode, the AI will suggest actions for your approval.",
        title="Help",
        border_style=COLOR_INFO,
        expand=False
    )) 