"""
File operations utility module for reading, writing, and searching files.
"""
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

def read_file(file_path: str, start_line: int = 0, end_line: Optional[int] = None) -> Tuple[str, int]:
    """
    Read a file and return its contents.
    
    Args:
        file_path: Path to the file
        start_line: Line to start reading from (0-indexed)
        end_line: Line to end reading at (0-indexed, inclusive)
        
    Returns:
        Tuple of (file contents as string, total line count)
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            total_lines = len(lines)
            
            if end_line is None:
                end_line = total_lines
                
            # Ensure bounds are valid
            start_line = max(0, min(start_line, total_lines - 1))
            end_line = max(start_line, min(end_line, total_lines))
            
            return ''.join(lines[start_line:end_line]), total_lines
    except Exception as e:
        return f"Error reading file: {str(e)}", 0

def write_file(file_path: str, content: str, create_dirs: bool = True) -> str:
    """
    Write content to a file.
    
    Args:
        file_path: Path to the file
        content: Content to write
        create_dirs: Create parent directories if they don't exist
        
    Returns:
        Success or error message
    """
    try:
        if create_dirs:
            os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
            
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return f"Successfully wrote to {file_path}"
    except Exception as e:
        return f"Error writing to file: {str(e)}"

def edit_file(file_path: str, new_content: str, start_line: int = 0, end_line: Optional[int] = None) -> str:
    """
    Edit a section of a file.
    
    Args:
        file_path: Path to the file
        new_content: New content to insert
        start_line: Line to start editing from (0-indexed)
        end_line: Line to end editing at (0-indexed, inclusive)
        
    Returns:
        Success or error message
    """
    try:
        # Read the existing file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Determine end_line if not specified
        if end_line is None:
            end_line = start_line
            
        # Ensure bounds are valid
        total_lines = len(lines)
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
    except Exception as e:
        return f"Error editing file: {str(e)}"

def list_files(directory: str, pattern: Optional[str] = None) -> List[str]:
    """
    List files in a directory, optionally matching a pattern.
    
    Args:
        directory: Directory to list files from
        pattern: Optional regex pattern to match filenames against
        
    Returns:
        List of file paths
    """
    try:
        files = []
        for root, _, filenames in os.walk(directory):
            for filename in filenames:
                file_path = os.path.join(root, filename)
                if pattern is None or re.search(pattern, file_path):
                    files.append(file_path)
        return files
    except Exception as e:
        print(f"Error listing files: {str(e)}")
        return []

def search_in_file(file_path: str, pattern: str) -> List[Tuple[int, str]]:
    """
    Search for a pattern in a file.
    
    Args:
        file_path: Path to the file
        pattern: Regex pattern to search for
        
    Returns:
        List of tuples (line_number, line_content) for matching lines
    """
    try:
        matches = []
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if re.search(pattern, line):
                    matches.append((i, line.strip()))
        return matches
    except Exception as e:
        print(f"Error searching in file {file_path}: {str(e)}")
        return []

def search_in_directory(directory: str, pattern: str, file_pattern: Optional[str] = None) -> List[Tuple[str, int, str]]:
    """
    Search for a pattern in all files in a directory.
    
    Args:
        directory: Directory to search in
        pattern: Regex pattern to search for in file contents
        file_pattern: Optional regex pattern to filter files by name
        
    Returns:
        List of tuples (file_path, line_number, line_content) for matching lines
    """
    results = []
    files = list_files(directory, file_pattern)
    
    for file_path in files:
        file_matches = search_in_file(file_path, pattern)
        for line_num, line_content in file_matches:
            results.append((file_path, line_num, line_content))
            
    return results

def get_file_info(file_path: str) -> dict:
    """
    Get information about a file.
    
    Args:
        file_path: Path to the file
        
    Returns:
        Dictionary with file information
    """
    try:
        path = Path(file_path)
        stats = path.stat()
        
        return {
            "exists": path.exists(),
            "is_file": path.is_file(),
            "is_dir": path.is_dir(),
            "size": stats.st_size if path.exists() else 0,
            "modified": stats.st_mtime if path.exists() else 0,
            "extension": path.suffix,
            "absolute_path": path.absolute().as_posix()
        }
    except Exception as e:
        print(f"Error getting file info: {str(e)}")
        return {
            "exists": False,
            "error": str(e)
        } 