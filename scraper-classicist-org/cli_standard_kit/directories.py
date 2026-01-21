"""Directory management for CLI applications."""

from pathlib import Path
from typing import Dict


def setup_directories(base_path: Path = None) -> Dict[str, Path]:
    """Setup standard directory structure for CLI applications.
    
    Creates and returns the following directory structure:
    - inputs/: Input files
    - outputs/: Output files
    - inputs/processed/: Successfully processed files
    - inputs/failed/: Failed files
    - logs/: Log files
    
    Args:
        base_path: Base directory path (defaults to current working directory)
    
    Returns:
        Dictionary with all directory paths keyed by name
    """
    if base_path is None:
        base_path = Path.cwd()
    
    dirs = {
        'inputs': base_path / 'inputs',
        'outputs': base_path / 'outputs',
        'processed': base_path / 'inputs' / 'processed',
        'failed': base_path / 'inputs' / 'failed',
        'logs': base_path / 'logs',
    }
    
    # Create all directories
    for dir_path in dirs.values():
        dir_path.mkdir(parents=True, exist_ok=True)
    
    return dirs


def get_timestamped_dir(base_dir: Path, prefix: str = "output") -> Path:
    """Create a timestamped subdirectory.
    
    Args:
        base_dir: Parent directory
        prefix: Prefix for the subdirectory name
    
    Returns:
        Path to the created timestamped directory
    """
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    dir_path = base_dir / f"{prefix}_{timestamp}"
    dir_path.mkdir(parents=True, exist_ok=True)
    
    return dir_path
