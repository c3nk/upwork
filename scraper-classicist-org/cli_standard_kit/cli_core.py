"""Core CLI framework for managing commands and argument parsing."""

import argparse
import sys
from typing import Dict, Optional

from .command_base import BaseCommand


class StandardCLI:
    """Main CLI framework that manages argparse and command execution.
    
    This class provides a unified interface for registering commands and
    handling argument parsing. It uses argparse internally and supports
    subcommands.
    
    Example:
        cli = StandardCLI(prog="mytool", description="My CLI tool")
        cli.register(MyCommand())
        cli.run()
    """
    
    def __init__(
        self,
        prog: str,
        description: Optional[str] = None,
        epilog: Optional[str] = None,
        formatter_class: Optional[argparse.HelpFormatter] = None,
    ) -> None:
        """Initialize the CLI framework.
        
        Args:
            prog: Program name (shown in help)
            description: Program description
            epilog: Text shown after help
            formatter_class: Custom help formatter (defaults to RawDescriptionHelpFormatter)
        """
        self.prog = prog
        self.description = description
        self.epilog = epilog
        self.formatter_class = formatter_class or argparse.RawDescriptionHelpFormatter
        self._commands: Dict[str, BaseCommand] = {}
        self._parser: Optional[argparse.ArgumentParser] = None
    
    def register(self, command: BaseCommand) -> None:
        """Register a command with the CLI.
        
        Args:
            command: BaseCommand instance to register
            
        Raises:
            ValueError: If command name is already registered
        """
        if command.name in self._commands:
            raise ValueError(f"Command '{command.name}' is already registered")
        
        if not command.name:
            raise ValueError("Command must have a non-empty 'name' attribute")
        
        self._commands[command.name] = command
    
    def _build_parser(self) -> argparse.ArgumentParser:
        """Build argument parser with all commands."""
        parser = argparse.ArgumentParser(
            prog=self.prog,
            description=self.description,
            epilog=self.epilog,
            formatter_class=self.formatter_class
        )
        
        # Add standard CLI options
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
            help="Show what would be done without actually doing it"
        )
        
        parser.add_argument(
            "--log-file",
            type=str,
            help="Save logs to file"
        )
        
        parser.add_argument(
            "--output", "-o",
            type=str,
            default="./outputs",
            help="Output directory (default: ./outputs)"
        )
        
        parser.add_argument(
            "--json",
            action="store_true",
            help="Output in JSON format"
        )
        
        parser.add_argument(
            "--version",
            action="version",
            version="%(prog)s 1.0.0"
        )
        
        # Add subparsers for commands
        if self._commands:
            subparsers = parser.add_subparsers(
                dest='command',
                help='Available commands',
                metavar='COMMAND'
            )
            
            # Add each command
            for cmd_name, command in self._commands.items():
                subparser = subparsers.add_parser(
                    cmd_name,
                    help=command.description,
                    description=command.description,
                    formatter_class=self.formatter_class
                )
                command.add_arguments(subparser)
        
        return parser
        
        subparsers = parser.add_subparsers(
            dest="command",
            help="Available commands",
            metavar="COMMAND",
        )
        
        for cmd in self._commands.values():
            subparser = subparsers.add_parser(
                cmd.name,
                help=cmd.description,
                description=cmd.description,
                formatter_class=self.formatter_class,
            )
            cmd.add_arguments(subparser)
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run the CLI with given arguments.
        
        Args:
            args: Command-line arguments (defaults to sys.argv[1:])
            
        Returns:
            Exit code from the executed command, or 0 if help was shown
        """
        if args is None:
            args = sys.argv[1:]
        
        self._parser = self._build_parser()
        parsed_args = self._parser.parse_args(args)
        
        # If no command provided and we have commands, show help
        if not hasattr(parsed_args, 'command') or parsed_args.command is None:
            if self._commands:
                self._parser.print_help()
                return 0
            # No commands registered, nothing to do
            return 0
        
        # Execute the selected command
        command = self._commands[parsed_args.command]
        return command.run(parsed_args)

