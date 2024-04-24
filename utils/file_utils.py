from pathlib import Path
import logging
import os
import importlib.util

def find_project_root():
    """
    Attempts to find the project root using multiple strategies.
    
    Returns:
        Path: The determined project root path.
    
    Raises:
        FileNotFoundError: If the project root cannot be determined.
    """
    # Strategy 1: Look for a .root marker file
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if (parent / '.root').exists():
            return parent

    # Strategy 2: Common marker files (e.g., .git directory, pyproject.toml)
    marker_files = ['.git', 'pyproject.toml', 'setup.py']
    current_path = Path(__file__).resolve()
    for parent in current_path.parents:
        if any((parent / marker).exists() for marker in marker_files):
            return parent

    # Strategy 3: Known package name, using 'augmentation' package located at the project root
    package_name = 'augmentation'
    spec = importlib.util.find_spec(package_name)
    if spec and spec.origin:
        package_path = Path(spec.origin).resolve()
        root_path = package_path.parent if package_path.name == '__init__.py' else package_path
        return root_path

    # Strategy 4: Fallback to current working directory
    return Path.cwd()

def get_dir(relative_path, return_as_string=True, project_root=None):
    """
    Generates an absolute path to a file or directory within the project.
    
    Args:
        relative_path (str or Path): The relative path within the project from the root directory.
        return_as_string (bool): Whether to return the path as a string (True) or as a Path object (False).
        project_root (str or Path, optional): Specifies the project root directory directly. If not provided,
                                               the function attempts to locate it using multiple strategies.

    Returns:
        str or Path: The absolute path of the provided relative path within the project, based on return_as_string.

    Raises:
        TypeError: If relative_path is not a string or Path object.
        ValueError: If the resolved path attempts to navigate above the project root.
        FileNotFoundError: If the path or project root cannot be determined.
    """
    # Handle Path input
    if isinstance(relative_path, Path):
        relative_path = str(relative_path)

    # Validate input
    if not isinstance(relative_path, str):
        raise TypeError(f"relative_path must be a string, not {type(relative_path).__name__}")
    
    logging.debug(f"Getting directory for relative path: {relative_path}")

    # Normalize the input path
    relative_path = Path(relative_path).as_posix()  # Normalize path separators

    # If an absolute path is provided, return it directly
    if Path(relative_path).is_absolute():
        return str(relative_path) if return_as_string else Path(relative_path)

    # Determine the project root
    root_path = project_root if project_root else find_project_root()

    logging.debug(f"Using project root: {root_path}")

    # Construct and validate the full path
    full_path = (root_path / relative_path).resolve(strict=False)  # 'strict=False' allows handling symlinks as per requirement

    # Ensure the resolved path does not navigate above the root
    if not str(full_path).startswith(str(root_path)):
        raise ValueError("The resolved path attempts to navigate above the project root.")

    # Validate existence of the path
    if not full_path.exists():
        raise FileNotFoundError(f"The path {full_path} does not exist.")

    logging.debug(f"Returning full path: {full_path}")

    return str(full_path) if return_as_string else full_path
