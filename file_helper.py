import os
import json
from typing import List, Dict, Union, Optional
import pandas as pd

# Define the base directory for all file operations
BASE_DIR = "./agent_workbook"

def _ensure_base_dir_exists():
    """
    Ensures the base directory exists, creating it if necessary.
    """
    if not os.path.exists(BASE_DIR):
        os.makedirs(BASE_DIR)
        # Silent creation - don't print messages about creating directories

def _validate_path(path: str) -> str:
    """
    Validates that the path is within the allowed base directory.
    Returns the full absolute path if valid.
    """
    # Remove leading ./ if present
    if path.startswith('./'):
        path = path[2:]
    
    # Create the full path
    full_path = os.path.join(BASE_DIR, path)
    
    # Convert both paths to absolute for consistent comparison
    abs_full_path = os.path.abspath(full_path)
    abs_base_dir = os.path.abspath(BASE_DIR)
    
    # Check if the path is within the base directory
    if not abs_full_path.startswith(abs_base_dir):
        raise ValueError(f"Access denied: Can only access files within the agent workspace. Do not use '../' or absolute paths. Valid examples: 'notes.txt', 'data/results.csv', 'folder/subfolder/file.json'")
    
    return full_path
    
def read_file(file_path: str) -> str:
    """
    Reads content from a file in the agent_workbook directory.
    
    Args:
        file_path: Path to the file to read (relative to BASE_DIR)
        
    Returns:
        Contents of the file as a string
    """
    try:
        # Ensure base directory exists
        _ensure_base_dir_exists()
        
        # Validate and get the full path
        full_path = _validate_path(file_path)
        
        # Check if file exists
        if not os.path.exists(full_path):
            return f"The file '{file_path}' doesn't exist yet. You can create it using write_file. Examples of valid paths: 'notes.txt', 'data/results.csv', 'folder/subfolder/file.json'"
        
        # Read the file content
        with open(full_path, 'r') as f:
            content = f.read()
            
        return content
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error reading file: {str(e)}. Examples of valid paths: 'notes.txt', 'data/results.csv', 'folder/subfolder/file.json'"

def write_file(file_path: str, content: str) -> str:
    """
    Writes content to a file in the agent_workbook directory.
    Creates the file if it doesn't exist, or overwrites if it does.
    
    Args:
        file_path: Path to the file to write (relative to BASE_DIR)
        content: Content to write to the file
        
    Returns:
        Status message indicating success or failure
    """
    try:
        # Ensure base directory exists
        _ensure_base_dir_exists()
        
        # Validate and get the full path
        full_path = _validate_path(file_path)
        
        # Create parent directories if they don't exist
        dir_name = os.path.dirname(full_path)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
        
        # Write the content to the file
        with open(full_path, 'w') as f:
            f.write(content)
            
        return f"Successfully wrote to file: {file_path}"
    except ValueError as e:
        return str(e)
    except Exception as e:
        return f"Error writing file: {str(e)}. Examples of valid paths: 'notes.txt', 'data/results.csv', 'folder/subfolder/file.json'"

def list_files(directory_path: str = "") -> List[str]:
    """
    Lists all files in a directory within the agent_workbook directory.
    
    Args:
        directory_path: Path to the directory to list files from (relative to BASE_DIR)
        
    Returns:
        List of file names in the directory
    """
    try:
        # Ensure base directory exists
        _ensure_base_dir_exists()
        
        # Validate and get the full path
        full_path = _validate_path(directory_path)
        
        # Create directory if it doesn't exist
        if not os.path.exists(full_path):
            os.makedirs(full_path, exist_ok=True)
            return ["Directory is empty. You can write files here. Examples of valid paths: 'notes.txt', 'data/results.csv', 'folder/subfolder/file.json'"]
            
        # Check if it's actually a directory
        if not os.path.isdir(full_path):
            return [f"'{directory_path}' is not a directory. Examples of valid directory paths: '', 'data', 'folder/subfolder'"]
        
        # List all files in the directory
        files = []
        for item in os.listdir(full_path):
            item_path = os.path.join(full_path, item)
            # Get path relative to BASE_DIR
            rel_path = os.path.relpath(item_path, BASE_DIR)
            files.append(rel_path)
        
        if not files:
            return ["Directory is empty. You can write files here. Examples of valid paths: 'notes.txt', 'data/results.csv', 'folder/subfolder/file.json'"]
            
        return files
    except ValueError as e:
        # Only return access denied errors
        return [str(e)]
    except Exception as e:
        # Hide other technical errors with a helpful message
        return ["Directory cannot be accessed. Examples of valid directory paths: '', 'data', 'folder/subfolder'"]