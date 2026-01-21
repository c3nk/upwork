"""
scraper-classicist-org - Web scraper for classicist.org with standardized CLI interface.

A package containing web scraping utilities and CLI commands for extracting data 
from classicist.org using the cli-standard-kit framework.
"""

__version__ = "0.1.0"
__author__ = "Cenk Kabahasanoglu"
__license__ = "MIT"

# Scraper module exports
from .commands import ScrapeCommand, ListCommand, ExportCommand
from .scraper_core import ClassicistScraper
from .parsers import HTMLParser, DataExtractor
from .exporters import DataExporter

__all__ = [
    # Commands
    'ScrapeCommand',
    'ListCommand', 
    'ExportCommand',
    # Core functionality
    'ClassicistScraper',
    'HTMLParser',
    'DataExtractor',
    'DataExporter',
]