"""Core scraping functionality for classicist.org using Playwright."""

import asyncio
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from playwright.async_api import async_playwright, Browser, Page, BrowserContext

from .parsers import HTMLParser, DataExtractor


class ClassicistScraper:
    """Main scraper class for classicist.org using Playwright."""

    def __init__(self,
                 delay: float = 2.0,
                 timeout: int = 30000,  # 30 seconds in ms
                 headless: bool = True,
                 logger=None,
                 output_dir: Optional[Path] = None):
        """Initialize the scraper.

        Args:
            delay: Delay between requests in seconds
            timeout: Request timeout in milliseconds
            headless: Whether to run browser in headless mode
            logger: Logger instance
            output_dir: Directory for debug output
        """
        self.delay = delay
        self.timeout = timeout
        self.headless = headless
        self.logger = logger
        self.output_dir = Path(output_dir) if output_dir else Path("./outputs")

        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None

        # Initialize components
        self.html_parser = HTMLParser()
        self.data_extractor = DataExtractor()

    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def initialize(self):
        """Initialize Playwright browser."""
        if self.logger:
            self.logger.info("Initializing Playwright browser...")

        self.playwright = await async_playwright().start()

        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu'
            ]
        )

        self.context = await self.browser.new_context(
            user_agent='scraper-classicist-org/0.1.0 (Educational Purpose)',
            viewport={'width': 1920, 'height': 1080}
        )

        if self.logger:
            self.logger.info("Browser initialized successfully")

    async def close(self):
        """Close browser and cleanup."""
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()

        if self.logger:
            self.logger.info("Browser closed")

    async def scrape_members_directory(self, url: str = "https://www.classicist.org/membership-directory/") -> Dict[str, Any]:
        """Scrape the membership directory listing.

        Args:
            url: Directory URL to scrape

        Returns:
            Dictionary containing all member information
        """
        if self.logger:
            self.logger.info(f"Starting scrape of membership directory: {url}")

        results = {
            'url': url,
            'timestamp': time.time(),
            'members': [],
            'errors': []
        }

        try:
            if not self.context:
                raise RuntimeError("Browser context not initialized")
            page = await self.context.new_page()

            # Set timeout
            page.set_default_timeout(self.timeout)

            if self.logger:
                self.logger.info(f"Navigating to {url}")

            # Navigate to the page
            await page.goto(url, wait_until='networkidle')

            # Wait for content to load
            await page.wait_for_timeout(2000)

            # Debug: Save screenshot and HTML for inspection
            if self.logger:
                try:
                    await page.screenshot(path=self.output_dir / "debug_screenshot.png")
                    html_content = await page.content()
                    with open(self.output_dir / "debug_page.html", 'w', encoding='utf-8') as f:
                        f.write(html_content)
                    self.logger.info("Debug files saved: debug_screenshot.png, debug_page.html")
                except Exception as e:
                    self.logger.warning(f"Failed to save debug files: {e}")

            # Extract member listings
            members_data = await self._extract_members_from_directory(page)

            if self.logger:
                self.logger.info(f"Found {len(members_data)} members in directory")

            # For now, just collect basic member info from directory
            # Detail scraping can be done separately to avoid overwhelming the server
            results['members'] = members_data

            if self.logger:
                self.logger.info(f"Collected {len(members_data)} members from directory listing")
                self.logger.info("Note: Detail scraping disabled. Use separate command for individual member details.")

            await page.close()

        except Exception as e:
            error_msg = f"Failed to scrape directory {url}: {str(e)}"
            results['errors'].append(error_msg)
            if self.logger:
                self.logger.exception(error_msg)

        if self.logger:
            self.logger.info(f"Directory scraping completed. Found {len(results['members'])} members, {len(results['errors'])} errors")

        return results

    async def _extract_members_from_directory(self, page: Page) -> List[Dict[str, Any]]:
        """Extract member information from the directory page.

        Args:
            page: Playwright page object

        Returns:
            List of member dictionaries
        """
        members = []

        # Wait for member listings to load
        await page.wait_for_timeout(1000)

        # Extract member data using JavaScript
        member_data = await page.evaluate("""
            () => {
                const members = [];

                // Look for member listing elements - based on actual page structure
                const memberElements = document.querySelectorAll('.list-item');

                memberElements.forEach(element => {
                    const member = {};

                    // Extract name from list-item-title-name
                    const nameElement = element.querySelector('.list-item-title-name a');
                    if (nameElement) {
                        member.name = nameElement.textContent.trim();
                        member.detail_url = nameElement.href;
                    }

                    // Extract field/classification from data attributes or text
                    const dataTitle = element.getAttribute('data-title');
                    if (dataTitle) {
                        member.data_title = dataTitle;
                    }

                    // Check for certified status - look for certified span
                    const certifiedElement = element.querySelector('.certified');
                    member.certified = certifiedElement !== null;

                    // Extract profession from class (profession-XXXX)
                    const classList = element.className.split(' ');
                    const professionClass = classList.find(cls => cls.startsWith('profession-'));
                    if (professionClass) {
                        member.profession_id = professionClass.replace('profession-', '');
                    }

                    // Extract chapter from class (chapter-XXXX)
                    const chapterClass = classList.find(cls => cls.startsWith('chapter-'));
                    if (chapterClass) {
                        member.chapter_id = chapterClass.replace('chapter-', '');
                    }

                    // Extract level from class (level-XXXX)
                    const levelClass = classList.find(cls => cls.startsWith('level-'));
                    if (levelClass) {
                        member.level_id = levelClass.replace('level-', '');
                    }

                    // Only add if we found at least a name
                    if (member.name) {
                        members.push(member);
                    }
                });

                return members;
            }
        """)

        return member_data

    async def _scrape_member_detail(self, url: str) -> Dict[str, Any]:
        """Scrape detailed information from individual member page.

        Args:
            url: Member detail page URL

        Returns:
            Dictionary with detailed member information
        """
        detail_data = {
            'about': '',
            'social_media': [],
            'photos': [],
            'logo': '',
            'highlights': []
        }

        try:
            if not self.context:
                raise RuntimeError("Browser context not initialized")
            page = await self.context.new_page()
            page.set_default_timeout(self.timeout)

            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(2000)

            # Extract detailed information
            detail_info = await page.evaluate("""
                () => {
                    const data = {
                        about: '',
                        social_media: [],
                        photos: [],
                        logo: '',
                        highlights: []
                    };

                    // Extract about section
                    const aboutElement = document.querySelector('.about, .description, .bio, [class*="about"], [class*="bio"]');
                    if (aboutElement) {
                        data.about = aboutElement.textContent.trim();
                    }

                    // Extract social media links
                    const socialLinks = document.querySelectorAll('a[href*="facebook"], a[href*="twitter"], a[href*="linkedin"], a[href*="instagram"], a[href*="youtube"]');
                    socialLinks.forEach(link => {
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

                    // Extract photos
                    const photoElements = document.querySelectorAll('img[src*="photo"], img[src*="image"], .photo, .image');
                    photoElements.forEach(img => {
                        if (img.src && !img.src.includes('logo')) {
                            data.photos.push({
                                url: img.src,
                                alt: img.alt || ''
                            });
                        }
                    });

                    // Extract logo
                    const logoElement = document.querySelector('img[src*="logo"], .logo img, [class*="logo"] img');
                    if (logoElement && logoElement.src) {
                        data.logo = logoElement.src;
                    }

                    // Extract highlights
                    const highlightElements = document.querySelectorAll('.highlight, .achievement, .award, [class*="highlight"]');
                    highlightElements.forEach(element => {
                        const highlight = element.textContent.trim();
                        if (highlight) {
                            data.highlights.push(highlight);
                        }
                    });

                    return data;
                }
            """)

            detail_data.update(detail_info)
            await page.close()

        except Exception as e:
            if self.logger:
                self.logger.warning(f"Failed to scrape member detail page {url}: {str(e)}")

        return detail_data

    async def scrape(self, url: str, depth: int = 1) -> Dict[str, Any]:
        """Scrape data from the given URL (legacy method for compatibility).

        Args:
            url: URL to scrape
            depth: Scraping depth

        Returns:
            Dictionary containing scraped data
        """
        if url == "https://www.classicist.org/membership-directory/" or "membership-directory" in url:
            return await self.scrape_members_directory(url)
        else:
            # For other URLs, use a generic scraping approach
            return await self._scrape_generic_page(url)

    async def _scrape_generic_page(self, url: str) -> Dict[str, Any]:
        """Scrape a generic page.

        Args:
            url: URL to scrape

        Returns:
            Dictionary containing page data
        """
        if self.logger:
            self.logger.info(f"Scraping generic page: {url}")

        results = {
            'url': url,
            'timestamp': time.time(),
            'data': [],
            'errors': []
        }

        try:
            if not self.context:
                raise RuntimeError("Browser context not initialized")

            page = await self.context.new_page()
            page.set_default_timeout(self.timeout)

            await page.goto(url, wait_until='networkidle')
            await page.wait_for_timeout(2000)

            # Extract basic page content
            page_data = await page.evaluate("""
                () => {
                    return {
                        url: window.location.href,
                        title: document.title,
                        content: document.body.innerText,
                        links: Array.from(document.querySelectorAll('a')).map(a => ({
                            text: a.textContent.trim(),
                            url: a.href
                        }))
                    };
                }
            """)

            results['data'].append(page_data)
            await page.close()

        except Exception as e:
            error_msg = f"Failed to scrape page {url}: {str(e)}"
            results['errors'].append(error_msg)
            if self.logger:
                self.logger.exception(error_msg)

        return results