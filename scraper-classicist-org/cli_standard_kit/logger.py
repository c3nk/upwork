"""Standardized logging configuration for CLI applications."""

import logging
from pathlib import Path
from datetime import datetime


def setup_logging(log_file: Path = None, verbose: bool = False,
                  quiet: bool = False) -> logging.Logger:
    """Setup logging to both file and console.
    
    Configuration:
    - VERBOSE mode: DEBUG level (detailed logging)
    - QUIET mode: ERROR level (only errors)
    - DEFAULT mode: INFO level (important events)
    
    File handler: Always DEBUG level (captures everything)
    Console handler: Respects verbose/quiet flags
    
    Args:
        log_file: Path to log file. If None, auto-generates in ./logs/
        verbose: Enable DEBUG level logging
        quiet: Suppress non-error output
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(__name__)
    logger.handlers.clear()
    logger.propagate = False
    
    # Auto-generate log file if not specified
    if log_file is None:
        log_dir = Path("./logs")
        log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_dir / f"process_{timestamp}.log"
    else:
        log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine console log level based on flags
    if quiet:
        console_level = logging.ERROR
    elif verbose:
        console_level = logging.DEBUG
    else:
        console_level = logging.INFO
    
    logger.setLevel(logging.DEBUG)
    
    # Format: [TIMESTAMP] [LEVEL] message
    fmt = "%(asctime)s [%(levelname)s] %(message)s"
    date_fmt = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(fmt, datefmt=date_fmt)
    
    # File handler - captures everything at DEBUG level
    fh = logging.FileHandler(log_file, encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # Console handler - respects verbose/quiet flags
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    return logger


def get_logger(name: str = None) -> logging.Logger:
    """Get a logger instance (use after setup_logging has been called).
    
    Args:
        name: Logger name (defaults to module name)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)
