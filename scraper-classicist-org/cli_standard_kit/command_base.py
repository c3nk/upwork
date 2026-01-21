"""Base command class for CLI framework."""

from abc import ABC, abstractmethod
from argparse import ArgumentParser
from typing import Optional


class BaseCommand(ABC):
    """Base class for all CLI commands.
    
    Subclasses must implement:
    - name: str - The command name (used as subcommand)
    - description: Optional[str] - Command description for help
    - add_arguments(parser) - Add command-specific arguments
    - run(args) - Execute the command logic
    
    Example:
        class MyCommand(BaseCommand):
            name = "mycmd"
            description = "Does something useful"
            
            def add_arguments(self, parser: ArgumentParser) -> None:
                parser.add_argument("--flag", action="store_true")
            
            def run(self, args) -> int:
                print("Running my command")
                return 0
    """
    
    name: str
    description: Optional[str] = None
    
    @abstractmethod
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments to the parser.
        
        Args:
            parser: ArgumentParser instance for this command
        """
        pass
    
    @abstractmethod
    def run(self, args) -> int:
        """Execute the command logic.
        
        Args:
            args: Parsed arguments namespace
            
        Returns:
            Exit code (0 for success, non-zero for failure)
        """
        pass

