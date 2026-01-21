#!/usr/bin/env python3
"""Main entry point for scraper-classicist-org."""

import sys
from cli_standard_kit import StandardCLI
from scraper.commands import ScrapeCommand, ListCommand, ExportCommand


def main():
    """Main entry point for the scraper CLI."""
    cli = StandardCLI(
        "scraper-classicist", 
        "Web scraper for classicist.org with standardized CLI interface"
    )
    
    # Register commands
    cli.register(ScrapeCommand())
    cli.register(ListCommand())
    cli.register(ExportCommand())
    
    # Run the CLI
    return cli.run()


if __name__ == "__main__":
    sys.exit(main())