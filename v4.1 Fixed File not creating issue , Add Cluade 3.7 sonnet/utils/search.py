"""
Search utility for finding code, files, and patterns in a codebase.
"""
import os
import re
import subprocess
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import platform

from utils.terminal import run_command, check_command_exists
from utils.file_operations import search_in_directory

def fuzzy_search(query: str, directory: str, max_results: int = 50) -> List[str]:
    """
    Perform a fuzzy search for files matching the query.
    
    Args:
        query: Search query
        directory: Directory to search in
        max_results: Maximum number of results to return
        
    Returns:
        List of matching file paths
    """
    results = []
    query_lower = query.lower()
    
    for root, _, files in os.walk(directory):
        for file in files:
            if query_lower in file.lower():
                results.append(os.path.join(root, file))
                if len(results) >= max_results:
                    return results
    
    return results

def regex_search(pattern: str, directory: str, file_pattern: Optional[str] = None, 
                 max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Search for a regex pattern in files.
    
    Args:
        pattern: Regex pattern to search for
        directory: Directory to search in
        file_pattern: Optional pattern to filter files
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with match information
    """
    results = []
    matches = search_in_directory(directory, pattern, file_pattern)
    
    for file_path, line_num, line_content in matches[:max_results]:
        results.append({
            "file": file_path,
            "line": line_num + 1,  # Convert to 1-indexed
            "content": line_content,
            "matched": re.search(pattern, line_content).group(0) if re.search(pattern, line_content) else ""
        })
    
    return results

def ripgrep_search(pattern: str, directory: str, file_pattern: Optional[str] = None, 
                  case_sensitive: bool = False, max_results: int = 100) -> List[Dict[str, Any]]:
    """
    Use ripgrep to search for a pattern if available, falling back to regex_search.
    
    Args:
        pattern: Pattern to search for
        directory: Directory to search in
        file_pattern: Optional pattern to filter files
        case_sensitive: Whether the search should be case sensitive
        max_results: Maximum number of results to return
        
    Returns:
        List of dictionaries with match information
    """
    # Check if ripgrep is available
    if not check_command_exists("rg"):
        return regex_search(pattern, directory, file_pattern, max_results)
    
    # Build ripgrep command
    cmd = ["rg", "--json"]
    if not case_sensitive:
        cmd.append("-i")
    if file_pattern:
        cmd.extend(["-g", file_pattern])
    cmd.extend(["--max-count", str(max_results), pattern, directory])
    
    # Convert cmd list to string based on platform
    if platform.system() == "Windows":
        cmd_str = " ".join(f'"{arg}"' if " " in arg else arg for arg in cmd)
    else:
        cmd_str = " ".join(f"'{arg}'" if " " in arg else arg for arg in cmd)
    
    # Execute command
    return_code, stdout, stderr = run_command(cmd_str)
    
    if return_code != 0:
        # Fall back to regex search
        return regex_search(pattern, directory, file_pattern, max_results)
    
    # Parse ripgrep JSON output
    results = []
    for line in stdout.strip().split("\n"):
        if not line:
            continue
        
        try:
            # Try to parse ripgrep JSON format
            import json
            data = json.loads(line)
            
            if "type" in data and data["type"] == "match":
                match = data["data"]
                results.append({
                    "file": match["path"]["text"],
                    "line": match["line_number"],
                    "content": match["lines"]["text"].strip(),
                    "matched": match["submatches"][0]["match"]["text"] if match["submatches"] else ""
                })
        except:
            # If JSON parsing fails, try to parse the line manually
            parts = line.split(":")
            if len(parts) >= 3:
                file_path = parts[0]
                line_num = int(parts[1])
                content = ":".join(parts[2:]).strip()
                results.append({
                    "file": file_path,
                    "line": line_num,
                    "content": content,
                    "matched": re.search(pattern, content).group(0) if re.search(pattern, content) else ""
                })
    
    return results[:max_results]

def find_definition(symbol: str, directory: str, file_extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Find the definition of a symbol in the codebase.
    
    Args:
        symbol: Symbol to find the definition for
        directory: Directory to search in
        file_extensions: List of file extensions to search in
        
    Returns:
        List of dictionaries with definition information
    """
    # Default file extensions for common languages
    if file_extensions is None:
        file_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp"]
    
    # Define regex patterns to find definitions based on language idioms
    patterns = [
        # Python function/class definitions
        fr"(def|class)\s+{re.escape(symbol)}\s*[\(:]",
        # JavaScript/TypeScript function/class/variable definitions
        fr"(function|class|const|let|var)\s+{re.escape(symbol)}\s*[\(={{:]",
        # C/C++/Java function/class definitions
        fr"(\w+\s+)?\w+\s+{re.escape(symbol)}\s*\(",
        # Variable declarations
        fr"(\w+\s+)?{re.escape(symbol)}\s*=",
    ]
    
    results = []
    
    # Create file pattern for extensions
    file_pattern = None
    if file_extensions:
        file_pattern = r".*(" + "|".join(ext.replace(".", r"\.") for ext in file_extensions) + r")$"
    
    # Search for each pattern
    for pattern in patterns:
        matches = ripgrep_search(pattern, directory, file_pattern, case_sensitive=True)
        for match in matches:
            # Check if it's likely a definition not just a usage
            content = match["content"]
            if (f"def {symbol}" in content or 
                f"class {symbol}" in content or 
                f"function {symbol}" in content or
                re.search(fr"(const|let|var)\s+{re.escape(symbol)}", content) or
                re.search(fr"(\w+\s+)?\w+\s+{re.escape(symbol)}\s*\(", content)):
                
                # Add if not already in results
                if not any(r["file"] == match["file"] and r["line"] == match["line"] for r in results):
                    results.append(match)
    
    return results

def find_references(symbol: str, directory: str, file_extensions: List[str] = None) -> List[Dict[str, Any]]:
    """
    Find references to a symbol in the codebase.
    
    Args:
        symbol: Symbol to find references for
        directory: Directory to search in
        file_extensions: List of file extensions to search in
        
    Returns:
        List of dictionaries with reference information
    """
    # Default file extensions for common languages
    if file_extensions is None:
        file_extensions = [".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".c", ".cpp", ".h", ".hpp"]
    
    # Create file pattern for extensions
    file_pattern = None
    if file_extensions:
        file_pattern = r".*(" + "|".join(ext.replace(".", r"\.") for ext in file_extensions) + r")$"
    
    # Use word boundaries to find the exact symbol
    pattern = fr"\b{re.escape(symbol)}\b"
    
    # Find all references
    references = ripgrep_search(pattern, directory, file_pattern, case_sensitive=True)
    
    return references 