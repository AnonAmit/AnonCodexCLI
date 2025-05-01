"""
Permissions utility for handling file and command permissions.
"""
import os
import platform
import re
from pathlib import Path
from typing import List, Set, Optional

# Define safe directory patterns (e.g., project directories)
DEFAULT_SAFE_DIRS = [os.getcwd()]

# Potentially dangerous command patterns
DANGEROUS_COMMANDS = [
    r"\brm\s+-rf\b",  # Remove recursively with force
    r"\bdd\b",        # Disk destroyer
    r"\bmkfs\b",      # Make filesystem
    r"\bformat\b",    # Format drives
    r"^sudo",         # Sudo commands
    r"\bdel\s+/[sqa]", # Windows delete with switches
    r"\brmdir\s+/[sq]", # Windows rmdir with switches
    r">(>)?.*\.(sh|bat|ps1|cmd)", # Redirecting to executable files
    r"\bregedit\b",   # Windows registry editor
    r"\bgpedit\b",    # Windows group policy editor
]

# Safe command prefixes
SAFE_COMMANDS = [
    "ls", "dir", "cat", "type", "echo", "cd", "pwd", "git", "python", "pip", 
    "npm", "node", "grep", "find", "code", "mkdir", "touch"
]

class PermissionManager:
    def __init__(self, safe_dirs: Optional[List[str]] = None):
        """
        Initialize the PermissionManager.
        
        Args:
            safe_dirs: List of directories that are safe to access
        """
        self.safe_dirs = set(safe_dirs or DEFAULT_SAFE_DIRS)
        self.dangerous_command_patterns = [re.compile(pattern) for pattern in DANGEROUS_COMMANDS]
        
    def add_safe_dir(self, directory: str) -> None:
        """
        Add a directory to the safe directories list.
        
        Args:
            directory: Directory to add
        """
        self.safe_dirs.add(os.path.abspath(directory))
        
    def is_file_access_allowed(self, file_path: str) -> bool:
        """
        Check if access to a file is allowed.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if access is allowed, False otherwise
        """
        try:
            abs_path = os.path.abspath(file_path)
            path_obj = Path(abs_path)
            
            # Check if the file is in a safe directory
            for safe_dir in self.safe_dirs:
                safe_path = Path(safe_dir)
                if safe_path in path_obj.parents or safe_path == path_obj:
                    return True
                    
            return False
        except Exception:
            return False
            
    def is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is allowed to be executed.
        
        Args:
            command: Command to check
            
        Returns:
            True if the command is allowed, False otherwise
        """
        # Check if command starts with a safe prefix
        command_prefix = command.split()[0] if command else ""
        if command_prefix.lower() in SAFE_COMMANDS:
            return True
            
        # Check against dangerous patterns
        for pattern in self.dangerous_command_patterns:
            if pattern.search(command):
                return False
                
        # Further checks can be added here
                
        return True
        
    def sanitize_command(self, command: str) -> str:
        """
        Sanitize a command by removing dangerous parts.
        
        Args:
            command: Command to sanitize
            
        Returns:
            Sanitized command
        """
        # Remove semicolons and pipes which could chain commands
        sanitized = re.sub(r'[;&|]', '', command)
        
        # Remove redirection operators
        sanitized = re.sub(r'[><]', '', sanitized)
        
        # Remove backticks and $(command) syntax
        sanitized = re.sub(r'`.*?`', '', sanitized)
        sanitized = re.sub(r'\$\(.*?\)', '', sanitized)
        
        return sanitized.strip()
        
    def get_permission_status(self, resource: str, resource_type: str = "file") -> dict:
        """
        Get detailed permission status for a resource.
        
        Args:
            resource: Resource to check (file path or command)
            resource_type: Type of resource ('file' or 'command')
            
        Returns:
            Dictionary with permission details
        """
        if resource_type == "file":
            is_allowed = self.is_file_access_allowed(resource)
            return {
                "allowed": is_allowed,
                "resource": resource,
                "type": "file",
                "reason": "In safe directory" if is_allowed else "Outside safe directories",
                "safe_dirs": list(self.safe_dirs)
            }
        elif resource_type == "command":
            is_allowed = self.is_command_allowed(resource)
            return {
                "allowed": is_allowed,
                "resource": resource,
                "type": "command",
                "reason": "Safe command" if is_allowed else "Potentially dangerous command"
            }
        else:
            return {
                "allowed": False,
                "resource": resource,
                "type": resource_type,
                "reason": "Unknown resource type"
            }

# Create a default permission manager
default_permission_manager = PermissionManager() 