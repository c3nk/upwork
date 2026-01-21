"""File operations utilities for CLI applications."""

from pathlib import Path
from typing import Callable, Tuple, Dict, List
import logging


def process_batch_files(
    files: List[Path],
    process_fn: Callable[[Path], Tuple[bool, str]],
    dirs: Dict[str, Path],
    logger: logging.Logger,
    dry_run: bool = False,
    stop_on_error: bool = False
) -> Dict[str, int]:
    """Process multiple files with progress tracking.
    
    Automatically moves files to processed/ or failed/ folders based on result.
    """
    stats = {'processed': 0, 'failed': 0, 'total': len(files)}
    
    if len(files) == 0:
        return stats
    
    for idx, file_path in enumerate(files, 1):
        percentage = (idx / stats['total']) * 100
        print(f"\r📊 Processing: {idx}/{stats['total']} ({percentage:.1f}%)",
              end="", flush=True)
        
        try:
            if dry_run:
                logger.info(f"[DRY-RUN] Would process: {file_path.name}")
                stats['processed'] += 1
                continue
            
            # Call the processing function
            success, message = process_fn(file_path)
            
            if success:
                stats['processed'] += 1
                dest = dirs['processed'] / file_path.name
                file_path.rename(dest)
                logger.info(f"✅ {file_path.name}: {message}")
            
            else:
                stats['failed'] += 1
                dest = dirs['failed'] / file_path.name
                file_path.rename(dest)
                logger.error(f"❌ {file_path.name}: {message}")
                
                if stop_on_error:
                    break
        
        except Exception as e:
            stats['failed'] += 1
            dest = dirs['failed'] / file_path.name
            file_path.rename(dest)
            logger.error(f"❌ {file_path.name}: {e}")
            
            if stop_on_error:
                break
    
    print("\n")
    return stats


def get_files_recursive(
    path: Path,
    pattern: str = "*",
    file_types: List[str] = None
) -> List[Path]:
    """Get all files recursively from a path."""
    if not path.exists():
        return []
    
    files = []
    
    if file_types:
        for f in path.rglob("*"):
            if f.is_file() and f.suffix.lower() in [t.lower() for t in file_types]:
                files.append(f)
    else:
        files = [f for f in path.rglob(pattern) if f.is_file()]
    
    return sorted(files)


def get_output_filename(input_file: Path, suffix: str = "") -> Path:
    """Generate output filename with optional suffix."""
    stem = input_file.stem
    suffix_part = f"_{suffix}" if suffix else ""
    return input_file.parent / f"{stem}{suffix_part}{input_file.suffix}"


def safe_rename(source: Path, dest: Path, logger: logging.Logger = None) -> bool:
    """Safely rename/move a file."""
    try:
        dest.parent.mkdir(parents=True, exist_ok=True)
        source.rename(dest)
        if logger:
            logger.debug(f"Moved: {source.name} -> {dest}")
        return True
    except Exception as e:
        if logger:
            logger.error(f"Failed to move {source.name}: {e}")
        return False
