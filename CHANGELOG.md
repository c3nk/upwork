# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-01-XX

### Added
- **Core CLI Framework**: Introduced `StandardCLI` class for managing argparse and command execution
- **BaseCommand**: Abstract base class for creating CLI commands with `name`, `description`, `add_arguments()`, and `run()` methods
- **Command Registration**: `cli.register()` method for dynamically registering commands
- **Loader Utility**: `get_cli()` convenience function for quick CLI instantiation
- **Automatic Help**: CLI automatically shows help when no command is provided
- **Subcommand Support**: Full argparse subcommand support with automatic help generation

### Changed
- Package structure reorganized to support framework architecture
- Updated package metadata and classifiers

### Documentation
- Added comprehensive framework documentation
- Updated README with framework usage examples

## [1.0.2] - Previous

### Added
- Standardized logging utilities
- ANSI color utilities and message formatting
- Directory layout helpers
- File operations for batch processing
- Argument parser with consistent flags

## [1.0.0] - Initial Release

### Added
- Initial release with core utilities

[1.0.3]: https://github.com/c3nk/cli-standard-kit/compare/v1.0.2...v1.0.3

