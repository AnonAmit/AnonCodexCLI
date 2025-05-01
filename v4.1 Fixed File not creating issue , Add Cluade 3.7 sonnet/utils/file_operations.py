"""
File operations utility module for reading, writing, and searching files.
"""
import os
import re
import sys
from pathlib import Path
from typing import List, Optional, Tuple, Union

class FileOperationError(Exception):
    """Custom exception for file operations errors."""
    def __init__(self, message: str, error_type: str = "general", original_exception: Optional[Exception] = None):
        self.message = message
        self.error_type = error_type
        self.original_exception = original_exception
        super().__init__(self.message)
    
    def __str__(self):
        base_msg = f"{self.error_type}: {self.message}"
        if self.original_exception:
            return f"{base_msg} (Original error: {str(self.original_exception)})"
        return base_msg

def is_safe_path(file_path: str, base_directory: Optional[str] = None) -> Tuple[bool, str]:
    """
    Validate if a file path is safe to use.
    
    This function checks for:
    - Path traversal attacks using '..' 
    - Absolute paths when only relative paths are expected
    - Existence of the base directory
    - Other potentially unsafe path characteristics
    
    Args:
        file_path: Path to validate
        base_directory: Optional base directory to restrict file operations to
                       (defaults to current working directory)
    
    Returns:
        Tuple of (is_safe: bool, message: str)
    """
    try:
        # Default to current working directory if base_directory is not provided
        if base_directory is None:
            base_directory = os.getcwd()
        
        # Make sure base directory exists
        base_path = Path(base_directory).resolve()
        if not base_path.exists():
            return False, f"Base directory '{base_directory}' does not exist"
        
        # Normalize and resolve the file path
        file_abs_path = Path(file_path).resolve()
        
        # Check for path traversal attempts
        if '..' in Path(file_path).parts:
            return False, "Path contains potentially unsafe '..' components"
        
        # If we have a base directory restriction, make sure the path is within it
        if base_directory is not None:
            # Check if the file path is within the base directory
            if not str(file_abs_path).startswith(str(base_path)):
                return False, f"Path is outside the allowed base directory: {base_directory}"
        
        # Check for unsafe characters or patterns based on OS
        unsafe_patterns = {
            'win32': ['<', '>', ':', '"', '|', '?', '*'],
            'default': []  # Unix-like systems handle most characters fine
        }
        
        platform = sys.platform
        patterns = unsafe_patterns.get(platform, unsafe_patterns['default'])
        
        filename = os.path.basename(file_path)
        for pattern in patterns:
            if pattern in filename:
                return False, f"Filename contains unsafe character: {pattern}"
        
        # Add more checks as needed
        
        return True, "Path is safe"
    except Exception as e:
        return False, f"Error validating path: {str(e)}"

def read_file(file_path: str, start_line: int = 0, end_line: Optional[int] = None, 
              base_directory: Optional[str] = None) -> Tuple[str, int]:
    """
    Read a file and return its contents.
    
    Args:
        file_path: Path to the file
        start_line: Line to start reading from (0-indexed)
        end_line: Line to end reading at (0-indexed, inclusive)
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        Tuple of (file contents as string, total line count)
        
    Raises:
        FileOperationError: If file cannot be read due to permissions, not existing, etc.
    """
    # Validate the path first
    is_safe, message = is_safe_path(file_path, base_directory)
    if not is_safe:
        return f"Cannot read file: {message}", 0
    
    try:
        if not os.path.exists(file_path):
            raise FileOperationError(f"File not found: {file_path}", "not_found")
            
        if not os.path.isfile(file_path):
            raise FileOperationError(f"Not a file: {file_path}", "invalid_file_type")
            
        if not os.access(file_path, os.R_OK):
            raise FileOperationError(f"Permission denied: {file_path}", "access_denied")
            
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            if end_line is None:
                end_line = total_lines
                
            # Ensure bounds are valid
            start_line = max(0, min(start_line, total_lines - 1))
            end_line = max(start_line, min(end_line, total_lines))
            
            return ''.join(lines[start_line:end_line]), total_lines
    except FileOperationError as e:
        return f"{e}", 0
    except UnicodeDecodeError as e:
        return f"Error decoding file: File may not be text or may use a different encoding: {str(e)}", 0
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        elif isinstance(e, FileNotFoundError):
            error_type = "not_found"
        elif isinstance(e, IsADirectoryError):
            error_type = "is_directory"
        
        error = FileOperationError(f"Error reading file: {str(e)}", error_type, e)
        return f"{error}", 0

def write_file(file_path: str, content: str, create_dirs: bool = True, 
               base_directory: Optional[str] = None) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        create_dirs: Create parent directories if they don't exist
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        Success or error message
        
    Raises:
        FileOperationError: If file cannot be written due to permissions, disk space, etc.
    """
    # Validate the path first
    is_safe, message = is_safe_path(file_path, base_directory)
    if not is_safe:
        return f"Cannot write to file: {message}"
    
    try:
        if os.path.exists(file_path) and not os.access(file_path, os.W_OK):
            raise FileOperationError(f"Permission denied: {file_path}", "access_denied")
            
        if create_dirs:
            dir_path = os.path.dirname(os.path.abspath(file_path))
            try:
                os.makedirs(dir_path, exist_ok=True)
            except Exception as e:
                raise FileOperationError(f"Failed to create directories for {file_path}: {str(e)}", "directory_creation_failed", e)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except FileOperationError as e:
        return f"{e}"
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        elif isinstance(e, FileNotFoundError):
            error_type = "not_found"
        elif isinstance(e, IsADirectoryError):
            error_type = "is_directory"
        elif isinstance(e, IOError) and "No space left" in str(e):
            error_type = "disk_full"
        
        error = FileOperationError(f"Error writing to file: {str(e)}", error_type, e)
        return f"{error}"

def edit_file(file_path: str, new_content: str, start_line: int = 0, end_line: Optional[int] = None,
              base_directory: Optional[str] = None) -> str:
    """
    Edit a section of a file.
    
    Args:
        file_path: Path to the file
        new_content: New content to insert
        start_line: Line to start editing from (0-indexed)
        end_line: Line to end editing at (0-indexed, inclusive)
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        Success or error message
        
    Raises:
        FileOperationError: If file cannot be edited
    """
    # Validate the path first
    is_safe, message = is_safe_path(file_path, base_directory)
    if not is_safe:
        return f"Cannot edit file: {message}"
    
    try:
        if not os.path.exists(file_path):
            raise FileOperationError(f"File not found: {file_path}", "not_found")
            
        if not os.path.isfile(file_path):
            raise FileOperationError(f"Not a file: {file_path}", "invalid_file_type")
            
        if not os.access(file_path, os.R_OK | os.W_OK):
            raise FileOperationError(f"Permission denied: {file_path}", "access_denied")
            
        # Read the existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Determine end_line if not specified
        if end_line is None:
            end_line = start_line
            
        # Ensure bounds are valid
        total_lines = len(lines)
        if start_line > total_lines:
            raise FileOperationError(f"Start line {start_line} is beyond the end of file (total lines: {total_lines})", "invalid_line_range")
            
        start_line = max(0, min(start_line, total_lines))
        end_line = max(start_line, min(end_line, total_lines))
        
        # Split the new content into lines
        new_lines = new_content.splitlines(True)
        
        # Replace the specified lines
        lines[start_line:end_line] = new_lines
        
        # Write the modified content back to the file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(lines)
            
        return f"Successfully edited {file_path}"
    except FileOperationError as e:
        return f"{e}"
    except UnicodeDecodeError as e:
        return f"Error decoding file: File may not be text or may use a different encoding: {str(e)}"
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        elif isinstance(e, FileNotFoundError):
            error_type = "not_found"
        elif isinstance(e, IsADirectoryError):
            error_type = "is_directory"
        
        error = FileOperationError(f"Error editing file: {str(e)}", error_type, e)
        return f"{error}"

def list_files(directory: str, pattern: Optional[str] = None, 
               base_directory: Optional[str] = None) -> List[str]:
    """
    List files in a directory, optionally matching a pattern.
    
    Args:
        directory: Directory to list files from
        pattern: Optional regex pattern to match filenames against
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        List of file paths
        
    Raises:
        FileOperationError: If directory cannot be accessed
    """
    # Validate the path first
    is_safe, message = is_safe_path(directory, base_directory)
    if not is_safe:
        print(f"Cannot list files: {message}")
        return []
    
    try:
        if not os.path.exists(directory):
            raise FileOperationError(f"Directory not found: {directory}", "not_found")
            
        if not os.path.isdir(directory):
            raise FileOperationError(f"Not a directory: {directory}", "not_directory")
            
        if not os.access(directory, os.R_OK):
            raise FileOperationError(f"Permission denied: {directory}", "access_denied")
            
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if pattern is None or re.search(pattern, file_path):
                    files.append(file_path)
        return files
    except FileOperationError as e:
        print(f"{e}")
        return []
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        elif isinstance(e, FileNotFoundError):
            error_type = "not_found"
        elif isinstance(e, NotADirectoryError):
            error_type = "not_directory"
        
        error = FileOperationError(f"Error listing files: {str(e)}", error_type, e)
        print(f"{error}")
        return []

def search_in_file(file_path: str, pattern: str, 
                   base_directory: Optional[str] = None) -> List[Tuple[int, str]]:
    """
    Search for a pattern in a file.
    
    Args:
        file_path: Path to the file
        pattern: Regex pattern to search for
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        List of tuples (line_number, line_content) for matching lines
        
    Raises:
        FileOperationError: If file cannot be read
    """
    # Validate the path first
    is_safe, message = is_safe_path(file_path, base_directory)
    if not is_safe:
        print(f"Cannot search in file: {message}")
        return []
    
    try:
        if not os.path.exists(file_path):
            raise FileOperationError(f"File not found: {file_path}", "not_found")
            
        if not os.path.isfile(file_path):
            raise FileOperationError(f"Not a file: {file_path}", "invalid_file_type")
            
        if not os.access(file_path, os.R_OK):
            raise FileOperationError(f"Permission denied: {file_path}", "access_denied")
        
        try:
            re.compile(pattern)
        except re.error as e:
            raise FileOperationError(f"Invalid regex pattern: {str(e)}", "invalid_regex", e)
            
        matches = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if re.search(pattern, line):
                    matches.append((i, line.strip()))
        return matches
    except FileOperationError as e:
        print(f"{e}")
        return []
    except UnicodeDecodeError as e:
        print(f"Error decoding file: File may not be text or may use a different encoding: {str(e)}")
        return []
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        elif isinstance(e, FileNotFoundError):
            error_type = "not_found"
        elif isinstance(e, IsADirectoryError):
            error_type = "is_directory"
        
        error = FileOperationError(f"Error searching in file {file_path}: {str(e)}", error_type, e)
        print(f"{error}")
        return []

def search_in_directory(directory: str, pattern: str, file_pattern: Optional[str] = None,
                        base_directory: Optional[str] = None) -> List[Tuple[str, int, str]]:
    """
    Search for a pattern in all files in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Regex pattern to search for in file contents
        file_pattern: Optional regex pattern to filter files by name
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        List of tuples (file_path, line_number, line_content) for matching lines
        
    Raises:
        FileOperationError: If directory cannot be accessed
    """
    # Validate the path first
    is_safe, message = is_safe_path(directory, base_directory)
    if not is_safe:
        print(f"Cannot search in directory: {message}")
        return []
    
    try:
        if not os.path.exists(directory):
            raise FileOperationError(f"Directory not found: {directory}", "not_found")
            
        if not os.path.isdir(directory):
            raise FileOperationError(f"Not a directory: {directory}", "not_directory")
            
        if not os.access(directory, os.R_OK):
            raise FileOperationError(f"Permission denied: {directory}", "access_denied")
        
        try:
            re.compile(pattern)
            if file_pattern:
                re.compile(file_pattern)
        except re.error as e:
            raise FileOperationError(f"Invalid regex pattern: {str(e)}", "invalid_regex", e)
    
        results = []
        files = list_files(directory, file_pattern)
        
        for file_path in files:
            try:
                file_matches = search_in_file(file_path, pattern)
                for line_num, line_content in file_matches:
                    results.append((file_path, line_num, line_content))
            except Exception as e:
                # Continue searching other files even if one fails
                print(f"Error searching in {file_path}: {str(e)}")
                
        return results
    except FileOperationError as e:
        print(f"{e}")
        return []
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        elif isinstance(e, FileNotFoundError):
            error_type = "not_found"
        elif isinstance(e, NotADirectoryError):
            error_type = "not_directory"
        
        error = FileOperationError(f"Error searching in directory: {str(e)}", error_type, e)
        print(f"{error}")
        return []

def get_file_info(file_path: str, base_directory: Optional[str] = None) -> dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        base_directory: Optional base directory to restrict file operations to
        
    Returns:
        Dictionary with file information
        
    Raises:
        FileOperationError: If file info cannot be retrieved
    """
    # Validate the path first
    is_safe, message = is_safe_path(file_path, base_directory)
    if not is_safe:
        return {
            "exists": False,
            "error": message,
            "error_type": "unsafe_path"
        }
    
    try:
        path = Path(file_path)
        
        if not path.exists():
            return {
                "exists": False,
                "error": f"File not found: {file_path}",
                "error_type": "not_found"
            }
            
        if not os.access(file_path, os.R_OK):
            return {
                "exists": True,
                "error": f"Permission denied: {file_path}",
                "error_type": "access_denied",
                "is_file": path.is_file(),
                "is_dir": path.is_dir()
            }
            
        stats = path.stat()
        
        return {
            "exists": True,
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "size": stats.st_size,
            "modified": stats.st_mtime,
            "extension": path.suffix,
            "absolute_path": path.absolute().as_posix(),
            "parent_dir": path.parent.as_posix(),
            "readable": os.access(file_path, os.R_OK),
            "writable": os.access(file_path, os.W_OK),
            "executable": os.access(file_path, os.X_OK)
        }
    except Exception as e:
        error_type = "unknown"
        if isinstance(e, PermissionError):
            error_type = "permission_denied"
        
        return {
            "exists": False,
            "error": f"Error getting file info: {str(e)}",
            "error_type": error_type
        } 