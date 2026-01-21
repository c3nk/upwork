"""
cli_standard_kit - Reusable CLI utilities for consistent command-line interfaces.

A package containing common utilities for building standardized, professional 
Python CLI tools with consistent logging, coloring, directory management, 
and argument validation.
"""

__version__ = "1.0.3"
__author__ = "Cenk Kabahasanoglu"
__license__ = "MIT"

# Core CLI framework exports
from .command_base import BaseCommand
from .cli_core import StandardCLI
from .loader import get_cli

# Utility modules
from . import colors
from . import logger
from . import directories
from . import file_ops
from . import parser

__all__ = [
    # Core framework
    'BaseCommand',
    'StandardCLI',
    'get_cli',
    # Utilities
    'colors',
    'logger', 
    'directories',
    'file_ops',
    'parser',
]
