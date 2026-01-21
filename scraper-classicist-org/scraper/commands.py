"""CLI commands for scraper-classicist-org."""

import asyncio
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
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

        # Run the async scraping
        try:
            return asyncio.run(self._run_async(args, logger))
        except KeyboardInterrupt:
            print(MessageFormatter.warning("Scraping interrupted by user"), file=sys.stderr)
            if logger:
                logger.warning("Scraping interrupted by user")
            return 130
        except Exception as e:
            print(MessageFormatter.error(f"Scraping failed: {str(e)}"), file=sys.stderr)
            if logger:
                logger.exception("Scraping failed")
            return 1

    async def _run_async(self, args, logger) -> int:
        """Run the scraping asynchronously."""
        try:
            # Setup directories
            if args.output_dir:
                dirs = setup_directories(args.output_dir)
            else:
                dirs = setup_directories()

            print(MessageFormatter.process(f"Scraping {args.url}..."))

            # Initialize and run scraper
            async with ClassicistScraper(logger=logger, output_dir=dirs['outputs']) as scraper:
                # Perform scraping
                if "membership-directory" in args.url:
                    data = await scraper.scrape_members_directory(args.url)
                else:
                    data = await scraper.scrape(args.url, args.depth)

            # Export data
            exporter = DataExporter(dirs['outputs'], logger=logger)
            output_file = exporter.export(data, format=args.format)

            print(MessageFormatter.success(f"Scraping completed!"))
            print(f"Data exported to: {output_file}")

            if args.log_file:
                print(f"Log file: {args.log_file}")

            return 0

        except Exception as e:
            print(MessageFormatter.error(f"Scraping failed: {str(e)}"), file=sys.stderr)
            if logger:
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


class ScrapeDetailsCommand(BaseCommand):
    """Scrape detailed information for individual members."""

    name = "scrape-details"
    description = "Scrape detailed information for individual members"

    def add_arguments(self, parser: ArgumentParser) -> None:
        """Add command-specific arguments."""
        parser.add_argument(
            "--input-file",
            type=Path,
            required=True,
            help="CSV file containing member basic info"
        )
        parser.add_argument(
            "--limit",
            type=int,
            default=10,
            help="Maximum number of members to process (default: 10)"
        )
        parser.add_argument(
            "--start-from",
            type=int,
            default=0,
            help="Start processing from this row index (default: 0)"
        )
        parser.add_argument(
            "--output-dir",
            type=Path,
            help="Output directory for detailed data"
        )

    def run(self, args) -> int:
        """Execute detailed scraping command."""
        logger = setup_logging(args.log_file, args.verbose, args.quiet)

        # Run the async scraping
        try:
            return asyncio.run(self._run_details_async(args, logger))
        except KeyboardInterrupt:
            print(MessageFormatter.warning("Detail scraping interrupted by user"), file=sys.stderr)
            if logger:
                logger.warning("Detail scraping interrupted by user")
            return 130
        except Exception as e:
            print(MessageFormatter.error(f"Detail scraping failed: {str(e)}"), file=sys.stderr)
            if logger:
                logger.exception("Detail scraping failed")
            return 1

    async def _run_details_async(self, args, logger) -> int:
        """Run detailed scraping asynchronously."""
        try:
            # Setup directories
            if args.output_dir:
                dirs = setup_directories(args.output_dir)
            else:
                dirs = setup_directories()

            # Load member data from CSV
            import pandas as pd
            df = pd.read_csv(args.input_file)

            # Filter to members with detail URLs
            members_with_urls = df[df['detail_url'].notna()]

            if len(members_with_urls) == 0:
                print(MessageFormatter.warning("No members with detail URLs found"))
                return 1

            # Apply limits
            start_idx = args.start_from
            end_idx = min(start_idx + args.limit, len(members_with_urls))

            selected_members = members_with_urls.iloc[start_idx:end_idx]

            print(MessageFormatter.process(f"Scraping details for {len(selected_members)} members ({start_idx}-{end_idx-1})..."))

            # Initialize scraper
            async with ClassicistScraper(logger=logger, output_dir=dirs['outputs']) as scraper:
                detailed_members = []

                for i, (_, member_row) in enumerate(selected_members.iterrows()):
                    member_name = member_row['name']
                    detail_url = member_row['detail_url']

                    try:
                        if logger:
                            logger.info(f"Scraping details for {member_name} ({i+1}/{len(selected_members)})")

                        print(f"Processing: {member_name}")

                        # Scrape member details
                        detail_data = await self._scrape_single_member_details(scraper, detail_url)

                        # Combine basic info with details
                        member_info = member_row.to_dict()
                        member_info.update(detail_data)
                        detailed_members.append(member_info)

                        # Add delay between requests
                        if i < len(selected_members) - 1:
                            await asyncio.sleep(2.0)  # 2 second delay

                    except Exception as e:
                        error_msg = f"Failed to scrape details for {member_name}: {str(e)}"
                        print(MessageFormatter.error(error_msg))
                        if logger:
                            logger.error(error_msg)
                        continue

            # Export detailed data
            import pandas as pd
            detailed_df = pd.DataFrame(detailed_members)
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            output_file = dirs['outputs'] / f"detailed_members_{timestamp}.csv"
            detailed_df.to_csv(output_file, index=False)

            print(MessageFormatter.success(f"Detail scraping completed!"))
            print(f"Processed {len(detailed_members)} members")
            print(f"Data exported to: {output_file}")

            return 0

        except Exception as e:
            print(MessageFormatter.error(f"Detail scraping failed: {str(e)}"), file=sys.stderr)
            if logger:
                logger.exception("Detail scraping failed")
            return 1

    async def _scrape_single_member_details(self, scraper: ClassicistScraper, url: str) -> Dict[str, Any]:
        """Scrape details for a single member."""
        detail_data = {}

        try:
            # Create a new page for this request
            if not scraper.context:
                raise RuntimeError("Browser context not initialized")

            page = await scraper.context.new_page()
            page.set_default_timeout(scraper.timeout)

            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(2000)

            # Extract detailed member information
            member_details = await page.evaluate("""
                () => {
                    const data = {
                        mailing_address: '',
                        phone: '',
                        email: '',
                        about: '',
                        social_media: [],
                        photos: [],
                        logo: '',
                        highlights: [],
                        field: '',
                        city: '',
                        state: ''
                    };

                    // Extract mailing address
                    const addressSelectors = [
                        '.address', '.mailing-address', '[class*="address"]',
                        '.location', '.contact', '[class*="contact"]'
                    ];
                    for (const selector of addressSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            data.mailing_address = element.textContent.trim();
                            break;
                        }
                    }

                    // Extract phone
                    const phoneSelectors = [
                        '.phone', '.telephone', '.tel', '[class*="phone"]',
                        'a[href^="tel:"]'
                    ];
                    for (const selector of phoneSelectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            data.phone = element.textContent.trim() ||
                                       element.getAttribute('href')?.replace('tel:', '');
                            if (data.phone) break;
                        }
                    }

                    // Extract email
                    const emailSelectors = [
                        '.email', '[class*="email"]',
                        'a[href^="mailto:"]'
                    ];
                    for (const selector of emailSelectors) {
                        const element = document.querySelector(selector);
                        if (element) {
                            data.email = element.textContent.trim() ||
                                       element.getAttribute('href')?.replace('mailto:', '');
                            if (data.email) break;
                        }
                    }

                    // Extract field/classification
                    const fieldSelectors = [
                        '.field', '.classification', '.profession', '.category',
                        '[class*="field"]', '[class*="class"]', '[class*="prof"]'
                    ];
                    for (const selector of fieldSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            data.field = element.textContent.trim();
                            break;
                        }
                    }

                    // Extract location (city, state)
                    const locationSelectors = [
                        '.location', '.city', '.address', '[class*="location"]'
                    ];
                    for (const selector of locationSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            const location = element.textContent.trim();
                            const parts = location.split(',');
                            if (parts.length >= 2) {
                                data.city = parts[0].trim();
                                data.state = parts[1].trim();
                            }
                            break;
                        }
                    }

                    // Extract about section
                    const aboutSelectors = [
                        '.about', '.description', '.bio', '.summary',
                        '[class*="about"]', '[class*="bio"]', '[class*="desc"]'
                    ];
                    for (const selector of aboutSelectors) {
                        const element = document.querySelector(selector);
                        if (element && element.textContent.trim()) {
                            data.about = element.textContent.trim();
                            break;
                        }
                    }

                    // Extract social media
                    const socialSelectors = [
                        'a[href*="facebook"]', 'a[href*="twitter"]', 'a[href*="linkedin"]',
                        'a[href*="instagram"]', 'a[href*="youtube"]', 'a[href*="social"]'
                    ];
                    socialSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(link => {
                            data.social_media.push({
                                platform: link.href.includes('facebook') ? 'facebook' :
                                         link.href.includes('twitter') ? 'twitter' :
                                         link.href.includes('linkedin') ? 'linkedin' :
                                         link.href.includes('instagram') ? 'instagram' :
                                         link.href.includes('youtube') ? 'youtube' : 'other',
                                url: link.href,
                                text: link.textContent.trim()
                            });
                        });
                    });

                    // Extract highlights/achievements
                    const highlightSelectors = [
                        '.highlight', '.achievement', '.award', '.feature',
                        '[class*="highlight"]', '[class*="award"]'
                    ];
                    highlightSelectors.forEach(selector => {
                        document.querySelectorAll(selector).forEach(element => {
                            const highlight = element.textContent.trim();
                            if (highlight) {
                                data.highlights.push(highlight);
                            }
                        });
                    });

                    // Extract logo
                    const logoSelectors = [
                        'img[src*="logo"]', '.logo img', '[class*="logo"] img'
                    ];
                    for (const selector of logoSelectors) {
                        const img = document.querySelector(selector);
                        if (img && img.src) {
                            data.logo = img.src;
                            break;
                        }
                    }

                    // Extract photos (excluding logo)
                    document.querySelectorAll('img').forEach(img => {
                        if (img.src && !img.src.includes('logo') &&
                            !img.src.includes('icon') && img.src.length > 10) {
                            data.photos.push({
                                url: img.src,
                                alt: img.alt || ''
                            });
                        }
                    });

                    return data;
                }
            """)

            detail_data.update(member_details)
            await page.close()

        except Exception as e:
            if scraper.logger:
                scraper.logger.warning(f"Failed to scrape member details from {url}: {str(e)}")

        return detail_data


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