# cli-standard-kit

Reusable CLI framework and utilities for consistent command-line interfaces in Python.

This package provides a complete framework and common building blocks for standardized, professional Python CLI tools:

## 🎯 Core Framework

- **StandardCLI**: Manage argparse and command execution with subcommand support
- **BaseCommand**: Abstract base class for creating reusable CLI commands
- **Command Registration**: Dynamically register commands with `cli.register()`
- **Automatic Help**: Built-in help generation for commands and subcommands

## 🛠️ Utilities

- Standardized logging (file + console) with verbose/quiet modes
- ANSI color utilities and message formatting templates
- Conventional directory layout helpers
- File operations for batch processing with progress tracking
- Argument parser with a consistent set of flags
- Pure Python (stdlib only, argparse-based)

## Installation

### From PyPI

```bash
pip install cli-standard-kit
```

### Development (editable)

```bash
git clone https://github.com/c3nk/cli-standard-kit.git
cd cli-standard-kit
pip install -e .
```

## Quick Start

### Using the Framework

Create a CLI with commands using the framework:

```python
from cli_standard_kit import StandardCLI, BaseCommand
from argparse import ArgumentParser

class ListCommand(BaseCommand):
    name = "list"
    description = "List items"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("--all", action="store_true", help="Show all items")
    
    def run(self, args) -> int:
        print("Listing items...")
        if args.all:
            print("All items")
        return 0

class CreateCommand(BaseCommand):
    name = "create"
    description = "Create a new item"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        parser.add_argument("name", help="Item name")
    
    def run(self, args) -> int:
        print(f"Creating {args.name}...")
        return 0

def main():
    cli = StandardCLI("mytool", "My awesome CLI tool")
    cli.register(ListCommand())
    cli.register(CreateCommand())
    return cli.run()

if __name__ == "__main__":
    exit(main())
```

Usage:
```bash
mytool list --all
mytool create myitem
mytool --help
```

### Using Utilities Only

Below is a minimal CLI using cli-standard-kit utility components.

```python
import sys
from pathlib import Path
from cli_standard_kit.parser import create_standard_parser, validate_arguments
from cli_standard_kit.logger import setup_logging
from cli_standard_kit.directories import setup_directories
from cli_standard_kit.colors import MessageFormatter
from cli_standard_kit.file_ops import get_files_recursive, process_batch_files


def process_file(file_path: Path) -> tuple[bool, str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            _ = f.read()
        return True, "Processed successfully"
    except Exception as e:
        return False, str(e)


def main() -> int:
    parser = create_standard_parser(
        prog="my-tool",
        description="My awesome CLI tool",
        version="1.0.0",
        epilog="Examples:\n  my-tool ./inputs --output ./outputs",
    )
    args = parser.parse_args()

    errors = validate_arguments(args)
    if errors:
        for error in errors:
            print(MessageFormatter.error(error), file=sys.stderr)
        return 1

    logger = setup_logging(args.log_file, args.verbose, args.quiet)
    dirs = setup_directories(Path.cwd())

    logger.info("Starting my-tool")

    try:
        input_files: list[Path] = []
        for p in args.paths:
            input_files.extend(get_files_recursive(p))

        if not input_files:
            print(MessageFormatter.warning("No files found to process"))
            return 0

        print(MessageFormatter.process(f"Found {len(input_files)} files"))

        stats = process_batch_files(
            input_files,
            process_file,
            dirs,
            logger,
            dry_run=args.dry_run,
        )

        print("\n" + "=" * 70)
        if args.dry_run:
            print(MessageFormatter.dry_run(f"Would process: {stats['processed']} files"))
        else:
            if stats["failed"] > 0:
                print(
                    MessageFormatter.warning(
                        f"Processed: {stats['processed']}, Failed: {stats['failed']}"
                    )
                )
            else:
                print(
                    MessageFormatter.success(
                        f"All {stats['processed']} files processed successfully"
                    )
                )

        print("=" * 70 + "\n")
        if args.log_file:
            print(f"Log file: {args.log_file}")
        return 0

    except KeyboardInterrupt:
        print(MessageFormatter.warning("Interrupted by user"), file=sys.stderr)
        logger.warning("Interrupted by user")
        return 130
    except Exception as e:
        print(MessageFormatter.error(str(e)), file=sys.stderr)
        logger.exception("Fatal error")
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

## Framework API

### StandardCLI

```python
from cli_standard_kit import StandardCLI, BaseCommand

cli = StandardCLI(
    prog="mytool",
    description="My CLI tool",
    epilog="See https://example.com for more info"
)

# Register commands
cli.register(MyCommand())

# Run CLI
exit_code = cli.run()
```

### BaseCommand

```python
from cli_commons import BaseCommand
from argparse import ArgumentParser

class MyCommand(BaseCommand):
    name = "mycmd"  # Required: command name
    description = "Does something"  # Optional: shown in help
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument("--flag", action="store_true")
        parser.add_argument("input", help="Input file")
    
    def run(self, args) -> int:
        """Execute command logic. Return 0 for success, non-zero for error."""
        print(f"Processing {args.input}")
        return 0
```

### get_cli() Helper

```python
from cli_commons import get_cli

cli = get_cli("mytool", "My tool description")
cli.register(MyCommand())
cli.run()
```

## Utility Modules

### colors.py

```python
from cli_standard_kit.colors import Colors, MessageFormatter

print(f"{Colors.GREEN}Success{Colors.END}")
print(MessageFormatter.success("Operation completed"))
print(MessageFormatter.error("Something failed"))
print(MessageFormatter.warning("Be careful"))
```

### logger.py

```python
from pathlib import Path
from cli_standard_kit.logger import setup_logging

logger = setup_logging()  # creates ./logs/process_<timestamp>.log
logger = setup_logging(verbose=True)
logger = setup_logging(quiet=True)
logger = setup_logging(log_file=Path("./my.log"))

logger.info("Information message")
logger.debug("Debug message")
logger.warning("Warning message")
logger.error("Error message")
```

### directories.py

```python
from pathlib import Path
from cli_standard_kit.directories import setup_directories, get_timestamped_dir

dirs = setup_directories()  # inputs/, outputs/, inputs/processed/, inputs/failed/, logs/
timestamped = get_timestamped_dir(Path("./outputs"), prefix="run")
```

### file_ops.py

```python
from pathlib import Path
from cli_standard_kit.file_ops import (
    process_batch_files,
    get_files_recursive,
    get_output_filename,
    safe_rename,
)

def process_file(file_path: Path) -> tuple[bool, str]:
    return True, "Success"

files = get_files_recursive(Path("./inputs"), pattern="*.txt")
stats = process_batch_files(files, process_file, dirs, logger, dry_run=False)
output = get_output_filename(Path("file.txt"), suffix="processed")  # file_processed.txt
safe_rename(Path("old.txt"), Path("new.txt"), logger)
```

### parser.py

```python
from cli_standard_kit.parser import (
    create_standard_parser,
    validate_arguments,
    validate_paths,
    validate_output_dir,
)

parser = create_standard_parser(
    prog="my-tool",
    description="What this tool does",
    version="1.0.0",
    epilog="Examples:\n  my-tool ./input",
)
args = parser.parse_args()

errors = validate_arguments(args)
if errors:
    for error in errors:
        print(error)
    sys.exit(1)
```

## Standard Flags

| Flag | Short | Description |
|------|-------|-------------|
| --help | -h | Show help message |
| --version |  | Show version |
| --verbose | -v | Enable verbose output (DEBUG) |
| --quiet | -q | Suppress output (ERROR only) |
| --dry-run | -n | Show what would be done |
| --log-file |  | Save logs to file |
| --output | -o | Output directory (default: ./outputs) |
| --json |  | JSON format output |

## Directory Structure

Created by `setup_directories()`:

```
project/
├── inputs/
├── outputs/
├── inputs/processed/
├── inputs/failed/
└── logs/
```

## Requirements

- Python 3.9 or higher
- No external dependencies (stdlib only)

## License

MIT

## Roadmap

### Core Features (Planned)

- **Auto Command Discovery**: Automatically discover and register commands from a directory
- **Global Flags**: Add `--verbose`, `--quiet`, `--dry-run` flags available to all commands
- **Command Aliases**: Support short names for commands (e.g., `ls` → `list`)
- **Command Groups**: Organize commands into groups (e.g., `db:migrate`, `db:seed`)

### Advanced Features (Planned)

- **Middleware/Hooks System**: Pre/post command execution hooks for logging, timing, authentication
- **Configuration File Support**: Load settings from YAML/JSON/TOML config files
- **Enhanced Error Handling**: Centralized exception handling with user-friendly error messages
- **Progress Indicators**: Progress bars and spinners for long-running operations

### Developer Experience (Planned)

- **Command Metadata**: Rich command metadata (version, author, examples) for enhanced help
- **Testing Utilities**: Mock helpers and testing framework for CLI commands
- **Tab Completion**: Bash/Zsh tab completion scripts for commands and arguments
- **Plugin System**: Support for external plugins and extensible architecture

### Utility Enhancements (Planned)

- **Table/Formatter Utilities**: Table formatting and JSON/CSV export utilities
- **Interactive Prompts**: User input prompts and confirmation dialogs
- **File Watchers**: File change monitoring and auto-reload functionality

See [CHANGELOG.md](CHANGELOG.md) for version history and recent changes.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT


