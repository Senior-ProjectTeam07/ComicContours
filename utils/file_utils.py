# file_utils.py

from pathlib import Path

def get_dir(relative_path):
    """
    Generates an absolute path to a file or directory within the project.
    
    Args:
    relative_path (str): The relative path within the project from the root directory.

    Returns:
    str: The absolute path of the provided relative path within the project.
    """
    # Start from the current file location
    current_path = Path(__file__).resolve()

    # Traverse up to find the marker file that indicates the root of the project
    root_path = current_path.parent.parent  # Go up two levels from the utils package
    for parent in root_path.parents:  # Traverse up to find the root
        if (parent / '.root').exists():
            root_path = parent
            break

    # Combine the root directory with the relative path and resolve to an absolute path
    full_path = (root_path / relative_path).resolve()

    # Check if the path exists
    if not full_path.exists():
        raise FileNotFoundError(f"The path {full_path} does not exist.")

    return str(full_path)
