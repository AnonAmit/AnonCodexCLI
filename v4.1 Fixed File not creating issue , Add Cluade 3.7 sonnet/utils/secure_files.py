"""
Secure file operations module that integrates file operations with permission checks.
"""
import os
from typing import List, Tuple, Optional, Union, Dict

from utils.file_operations import (
    is_safe_path, read_file, write_file, edit_file, 
    list_files, search_in_file, search_in_directory, get_file_info
)
from utils.permissions import default_permission_manager

class SecureFileHandler:
    """
    Secure file handler that integrates file operations with permission checks.
    """
    
    def __init__(self, base_directory: Optional[str] = None):
        """
        Initialize the secure file handler.
        
        Args:
            base_directory: Base directory to restrict file operations to
        """
        self.base_directory = base_directory or os.getcwd()
        self.permission_manager = default_permission_manager
        
        # Add base directory to safe dirs
        self.permission_manager.add_safe_dir(self.base_directory)
        
    def validate_path(self, file_path: str) -> Tuple[bool, str]:
        """
        Validate if a file path is safe to use and allowed by permissions.
        
        Args:
            file_path: Path to validate
            
        Returns:
            Tuple of (is_valid: bool, message: str)
        """
        # First check if path is safe (no traversal, etc.)
        is_safe, message = is_safe_path(file_path, self.base_directory)
        if not is_safe:
            return False, message
            
        # Then check permissions
        is_allowed = self.permission_manager.is_file_access_allowed(file_path)
        if not is_allowed:
            return False, "Access to this path is not allowed by permission settings"
            
        return True, "Path is valid and allowed"
        
    def read_file(self, file_path: str, start_line: int = 0, 
                  end_line: Optional[int] = None) -> Tuple[str, int]:
        """
        Read a file securely with permission validation.
        
        Args:
            file_path: Path to the file
            start_line: Line to start reading from (0-indexed)
            end_line: Line to end reading at (0-indexed, inclusive)
            
        Returns:
            Tuple of (file contents as string, total line count)
        """
        is_valid, message = self.validate_path(file_path)
        if not is_valid:
            return f"Cannot read file: {message}", 0
            
        return read_file(file_path, start_line, end_line, self.base_directory)
        
    def write_file(self, file_path: str, content: str, create_dirs: bool = True) -> str:
        """
        Write to a file securely with permission validation.
        
        Args:
            file_path: Path to the file
            content: Content to write
            create_dirs: Create parent directories if they don't exist
            
        Returns:
            Success or error message
        """
        is_valid, message = self.validate_path(file_path)
        if not is_valid:
            return f"Cannot write to file: {message}"
            
        # If creating directories, also validate the directory path
        if create_dirs:
            directory = os.path.dirname(os.path.abspath(file_path))
            if directory:
                is_dir_valid, dir_message = self.validate_path(directory)
                if not is_dir_valid:
                    return f"Cannot create directory: {dir_message}"
                    
        return write_file(file_path, content, create_dirs, self.base_directory)
        
    def edit_file(self, file_path: str, new_content: str, 
                  start_line: int = 0, end_line: Optional[int] = None) -> str:
        """
        Edit a file securely with permission validation.
        
        Args:
            file_path: Path to the file
            new_content: New content to insert
            start_line: Line to start editing from (0-indexed)
            end_line: Line to end editing at (0-indexed, inclusive)
            
        Returns:
            Success or error message
        """
        is_valid, message = self.validate_path(file_path)
        if not is_valid:
            return f"Cannot edit file: {message}"
            
        return edit_file(file_path, new_content, start_line, end_line, self.base_directory)
        
    def list_files(self, directory: str, pattern: Optional[str] = None) -> List[str]:
        """
        List files in a directory securely with permission validation.
        
        Args:
            directory: Directory to list files from
            pattern: Optional glob pattern to filter files
            
        Returns:
            List of file paths
        """
        is_valid, message = self.validate_path(directory)
        if not is_valid:
            return [f"Cannot list directory: {message}"]
            
        return list_files(directory, pattern, self.base_directory)
        
    def get_file_info(self, file_path: str) -> Dict:
        """
        Get file information securely with permission validation.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information
        """
        is_valid, message = self.validate_path(file_path)
        if not is_valid:
            return {"error": f"Cannot get file info: {message}"}
            
        return get_file_info(file_path, self.base_directory)


# Create a default secure file handler
default_secure_handler = SecureFileHandler()


# Convenience functions that use the default secure handler
def secure_read_file(file_path: str, start_line: int = 0, 
                    end_line: Optional[int] = None) -> Tuple[str, int]:
    """
    Convenience function to read a file securely using the default handler.
    """
    return default_secure_handler.read_file(file_path, start_line, end_line)
    
def secure_write_file(file_path: str, content: str, create_dirs: bool = True) -> str:
    """
    Convenience function to write to a file securely using the default handler.
    """
    return default_secure_handler.write_file(file_path, content, create_dirs)
    
def secure_edit_file(file_path: str, new_content: str, 
                    start_line: int = 0, end_line: Optional[int] = None) -> str:
    """
    Convenience function to edit a file securely using the default handler.
    """
    return default_secure_handler.edit_file(file_path, new_content, start_line, end_line)
    
def secure_list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    Convenience function to list files securely using the default handler.
    """
    return default_secure_handler.list_files(directory, pattern)
    
def secure_get_file_info(file_path: str) -> Dict:
    """
    Convenience function to get file information securely using the default handler.
    """
    return default_secure_handler.get_file_info(file_path) 