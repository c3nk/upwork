"""Argument parsing utilities for CLI applications."""

import argparse
from pathlib import Path
from typing import List


def create_standard_parser(
    prog: str,
    description: str,
    version: str = "1.0.0",
    epilog: str = None,
    positional_help: str = "Input paths (files or directories)"
) -> argparse.ArgumentParser:
    """Create a standard argument parser with common options."""
    parser = argparse.ArgumentParser(
        prog=prog,
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=epilog or ""
    )
    
    # Positional arguments
    parser.add_argument(
        "paths",
        nargs="+",
        type=Path,
        help=positional_help
    )
    
    # Standard options
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("./outputs"),
        help="Output directory (default: ./outputs)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output (DEBUG log level)"
    )
    
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress output except errors"
    )
    
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        default=None,
        help="Save detailed logs to file"
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}"
    )
    
    return parser


def validate_paths(paths: List[Path]) -> List[str]:
    """Validate that all paths exist."""
    errors = []
    
    for path in paths:
        if not path.exists():
            errors.append(f"Path does not exist: {path}")
    
    return errors


def validate_output_dir(output_path: Path) -> List[str]:
    """Validate output directory argument."""
    errors = []
    
    if output_path.exists() and not output_path.is_dir():
        errors.append(f"Output path is not a directory: {output_path}")
    
    return errors


def validate_arguments(args: argparse.Namespace) -> List[str]:
    """Validate all command-line arguments."""
    errors = []
    
    errors.extend(validate_paths(args.paths))
    errors.extend(validate_output_dir(args.output))
    
    if hasattr(args, 'verbose') and hasattr(args, 'quiet'):
        if args.verbose and args.quiet:
            errors.append("Cannot use both --verbose and --quiet")
    
    return errors
