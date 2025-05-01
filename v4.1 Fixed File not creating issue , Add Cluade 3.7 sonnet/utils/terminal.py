"""
Terminal command execution utility module.
"""
import os
import subprocess
import platform
import shlex
from typing import Tuple, Optional

def run_command(command: str, cwd: Optional[str] = None, timeout: int = 60) -> Tuple[int, str, str]:
    """
    Run a shell command and return its output.
    
    Args:
        command: Command to run
        cwd: Current working directory
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (return code, stdout, stderr)
    """
    try:
        # Handle command differently based on platform
        if platform.system() == "Windows":
            # For Windows, run through cmd.exe
            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                cwd=cwd,
                text=True
            )
        else:
            # For Unix-like systems, use shlex to properly split the command
            process = subprocess.Popen(
                shlex.split(command),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=cwd,
                text=True
            )
        
        # Wait for the process to complete with timeout
        stdout, stderr = process.communicate(timeout=timeout)
        return process.returncode, stdout, stderr
    
    except subprocess.TimeoutExpired:
        process.kill()
        return -1, "", "Command timed out after {timeout} seconds"
    except Exception as e:
        return -1, "", f"Error executing command: {str(e)}"

def get_os_info() -> dict:
    """
    Get information about the operating system.
    
    Returns:
        Dictionary with OS information
    """
    return {
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "is_windows": platform.system() == "Windows",
        "is_linux": platform.system() == "Linux",
        "is_mac": platform.system() == "Darwin"
    }

def check_command_exists(command: str) -> bool:
    """
    Check if a command exists in the system.
    
    Args:
        command: Command to check
        
    Returns:
        True if the command exists, False otherwise
    """
    if platform.system() == "Windows":
        check_cmd = f"where {command}"
    else:
        check_cmd = f"which {command}"
    
    return_code, _, _ = run_command(check_cmd)
    return return_code == 0

def get_command_output(command: str, cwd: Optional[str] = None) -> str:
    """
    Run a command and return its output, handling errors gracefully.
    
    Args:
        command: Command to run
        cwd: Current working directory
        
    Returns:
        Command output or error message
    """
    return_code, stdout, stderr = run_command(command, cwd)
    
    if return_code == 0:
        return stdout.strip()
    else:
        return f"Error (code {return_code}): {stderr.strip()}"

def run_background_command(command: str, cwd: Optional[str] = None) -> int:
    """
    Run a command in the background and return its process ID.
    
    Args:
        command: Command to run
        cwd: Current working directory
        
    Returns:
        Process ID or -1 on error
    """
    try:
        if platform.system() == "Windows":
            # For Windows, use start command
            cmd = f'start /b {command}'
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        else:
            # For Unix-like systems, append & to run in background
            cmd = f"{command} &"
            process = subprocess.Popen(
                cmd,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
        
        return process.pid
    except Exception as e:
        print(f"Error running background command: {str(e)}")
        return -1 