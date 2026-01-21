"""CLI commands for scraper-classicist-org."""

import sys
from pathlib import Path
from typing import List, Optional
from argparse import ArgumentParser

from cli_standard_kit import BaseCommand
from cli_standard_kit.colors import MessageFormatter
from cli_standard_kit.logger import setup_logging
from cli_standard_kit.directories import setup_directories

from .scraper_core import ClassicistScraper
from .exporters import DataExporter


class ScrapeCommand(BaseCommand):
    """Scrape data from classicist.org."""
    
    name = "scrape"
    description = "Scrape data from classicist.org"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--url",
            help="Specific URL to scrape (default: main site)",
            default="https://classicist.org/"
        )
        parser.add_argument(
            "--depth",
            type=int,
            default=1,
            help="Scraping depth (default: 1)"
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            help="Output directory for scraped data"
        )
        parser.add_argument(
            "--format",
            choices=["json", "csv", "excel"],
            default="json",
            help="Output format (default: json)"
        )
    
    def run(self, args) -> int:
        """Execute scraping command."""
        logger = setup_logging(args.log_file, args.verbose, args.quiet)
        
        try:
            # Setup directories
            if args.output_dir:
                dirs = setup_directories(args.output_dir)
            else:
                dirs = setup_directories()
            
            # Export data
            exporter = DataExporter(dirs['outputs'], logger=logger)
            
            print(MessageFormatter.process(f"Scraping {args.url}..."))
            
            # Initialize scraper
            scraper = ClassicistScraper(logger=logger)
            
            # Perform scraping
            data = scraper.scrape(
                url=args.url,
                depth=args.depth
            )
            
            # Export data
            exporter = DataExporter(dirs['outputs'], logger=logger)
            output_file = exporter.export(data, format=args.format)
            
            print(MessageFormatter.success(f"Scraping completed!"))
            print(f"Data exported to: {output_file}")
            
            if args.log_file:
                print(f"Log file: {args.log_file}")
            
            return 0
            
        except KeyboardInterrupt:
            print(MessageFormatter.warning("Scraping interrupted by user"), file=sys.stderr)
            logger.warning("Scraping interrupted by user")
            return 130
            
        except Exception as e:
            print(MessageFormatter.error(f"Scraping failed: {str(e)}"), file=sys.stderr)
            logger.exception("Scraping failed")
            return 1


class ListCommand(BaseCommand):
    """List available scraping targets or previously scraped data."""
    
    name = "list"
    description = "List available targets or scraped data"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--type",
            choices=["targets", "data"],
            default="targets",
            help="What to list (default: targets)"
        )
        parser.add_argument(
            "--data-dir",
            type=Path,
            help="Data directory to list (default: ./outputs)"
        )
    
    def run(self, args) -> int:
        """Execute list command."""
        logger = setup_logging(args.log_file, args.verbose, args.quiet)
        
        try:
            if args.type == "targets":
                self._list_targets()
            else:
                self._list_data(args.data_dir)
            
            return 0
            
        except Exception as e:
            print(MessageFormatter.error(f"List failed: {str(e)}"), file=sys.stderr)
            logger.exception("List failed")
            return 1
    
    def _list_targets(self):
        """List available scraping targets."""
        targets = [
            "https://classicist.org/",
            "https://classicist.org/issues/",
            "https://classicist.org/archives/",
            "https://classicist.org/about/"
        ]
        
        print(MessageFormatter.info("Available scraping targets:"))
        for i, target in enumerate(targets, 1):
            print(f"  {i}. {target}")
    
    def _list_data(self, data_dir: Optional[Path]):
        """List previously scraped data."""
        if data_dir is None:
            data_dir = Path("./outputs")
        
        if not data_dir.exists():
            print(MessageFormatter.warning("No data directory found"))
            return
        
        files = list(data_dir.glob("**/*"))
        if not files:
            print(MessageFormatter.warning("No data files found"))
            return
        
        print(MessageFormatter.info(f"Data files in {data_dir}:"))
        for file_path in sorted(files):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"  {file_path.relative_to(data_dir.parent)} ({size} bytes)")


class ExportCommand(BaseCommand):
    """Export scraped data in different formats."""
    
    name = "export"
    description = "Export scraped data to different formats"
    
    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "input_file",
            type=Path,
            help="Input data file to export"
        )
        parser.add_argument(
            "--format",
            choices=["json", "csv", "excel"],
            required=True,
            help="Export format"
        )
        parser.add_argument(
            "--output",
            type=Path,
            help="Output file path (default: auto-generated)"
        )
    
    def run(self, args) -> int:
        """Execute export command."""
        logger = setup_logging(args.log_file, args.verbose, args.quiet)
        
        try:
            # Validate input file
            if not args.input_file.exists():
                print(MessageFormatter.error(f"Input file not found: {args.input_file}"))
                return 1
            
            # Load data (simplified - in real implementation, would detect format)
            import json
            with open(args.input_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Export data
            if args.output:
                output_file = args.output
                output_dir = args.output.parent
            else:
                dirs = setup_directories()
                output_dir = dirs['outputs']
                output_file = None
            
            exporter = DataExporter(output_dir, logger=logger)
            result_file = exporter.export(data, format=args.format, output_file=output_file)
            
            print(MessageFormatter.success(f"Data exported to: {result_file}"))
            
            return 0
            
        except Exception as e:
            print(MessageFormatter.error(f"Export failed: {str(e)}"), file=sys.stderr)
            logger.exception("Export failed")
            return 1