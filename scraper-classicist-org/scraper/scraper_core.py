"""Core scraping functionality for classicist.org."""

import time
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

from .parsers import HTMLParser, DataExtractor


class ClassicistScraper:
    """Main scraper class for classicist.org."""
    
    def __init__(self, 
                 delay: float = 1.0,
                 timeout: int = 30,
                 user_agent: str = None,
                 logger=None):
        """Initialize the scraper.
        
        Args:
            delay: Delay between requests in seconds
            timeout: Request timeout in seconds
            user_agent: User agent string for requests
            logger: Logger instance
        """
        self.delay = delay
        self.timeout = timeout
        self.logger = logger
        
        # Setup session
        self.session = requests.Session()
        if user_agent:
            self.session.headers.update({'User-Agent': user_agent})
        else:
            self.session.headers.update({
                'User-Agent': 'scraper-classicist-org/0.1.0 (Educational Purpose)'
            })
        
        # Initialize components
        self.html_parser = HTMLParser()
        self.data_extractor = DataExtractor()
    
    def scrape(self, url: str, depth: int = 1) -> Dict[str, Any]:
        """Scrape data from the given URL.
        
        Args:
            url: URL to scrape
            depth: Scraping depth
            
        Returns:
            Dictionary containing scraped data
        """
        if self.logger:
            self.logger.info(f"Starting scrape of {url} at depth {depth}")
        
        results = {
            'url': url,
            'timestamp': time.time(),
            'depth': depth,
            'data': [],
            'errors': []
        }
        
        try:
            # Scrape the main URL
            page_data = self._scrape_page(url)
            results['data'].append(page_data)
            
            # If depth > 1, scrape linked pages
            if depth > 1:
                linked_urls = self._find_scrapable_links(page_data['content'], url)
                
                for link_url in linked_urls[:10]:  # Limit to avoid overwhelming
                    try:
                        linked_data = self._scrape_page(link_url)
                        results['data'].append(linked_data)
                        
                        # Be respectful - add delay
                        time.sleep(self.delay)
                        
                    except Exception as e:
                        error_msg = f"Failed to scrape {link_url}: {str(e)}"
                        results['errors'].append(error_msg)
                        if self.logger:
                            self.logger.warning(error_msg)
        
        except Exception as e:
            error_msg = f"Failed to scrape main URL {url}: {str(e)}"
            results['errors'].append(error_msg)
            if self.logger:
                self.logger.error(error_msg)
        
        if self.logger:
            self.logger.info(f"Scraping completed. Found {len(results['data'])} pages, {len(results['errors'])} errors")
        
        return results
    
    def _scrape_page(self, url: str) -> Dict[str, Any]:
        """Scrape a single page.
        
        Args:
            url: URL to scrape
            
        Returns:
            Dictionary containing page data
        """
        if self.logger:
            self.logger.debug(f"Scraping page: {url}")
        
        # Make request
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()
        
        # Parse HTML
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Extract basic page info
        page_data = {
            'url': url,
            'status_code': response.status_code,
            'content_type': response.headers.get('content-type', ''),
            'title': '',
            'content': '',
            'metadata': {},
            'links': [],
            'extracted_data': {}
        }
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            page_data['title'] = title_tag.get_text().strip()
        
        # Extract main content
        content = self.html_parser.extract_main_content(soup)
        page_data['content'] = content
        
        # Extract metadata
        page_data['metadata'] = self.html_parser.extract_metadata(soup)
        
        # Extract links
        page_data['links'] = self.html_parser.extract_links(soup, base_url=url)
        
        # Extract specific data based on page type
        page_data['extracted_data'] = self.data_extractor.extract_data(soup, url)
        
        return page_data
    
    def _find_scrapable_links(self, content: str, base_url: str) -> List[str]:
        """Find links that should be scraped.
        
        Args:
            content: HTML content
            base_url: Base URL for resolving relative links
            
        Returns:
            List of URLs to scrape
        """
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        
        # Look for specific patterns that indicate scrapable content
        selectors = [
            'a[href*="/issues/"]',
            'a[href*="/archives/"]',
            'a[href*="/article/"]',
            'a[href*="/post/"]'
        ]
        
        for selector in selectors:
            elements = soup.select(selector)
            for element in elements:
                href = element.get('href')
                if href:
                    full_url = urljoin(base_url, href)
                    if self._is_valid_target(full_url):
                        links.append(full_url)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def _is_valid_target(self, url: str) -> bool:
        """Check if URL is a valid scraping target.
        
        Args:
            url: URL to check
            
        Returns:
            True if URL should be scraped
        """
        parsed = urlparse(url)
        
        # Must be from classicist.org
        if 'classicist.org' not in parsed.netloc.lower():
            return False
        
        # Skip common non-content pages
        skip_patterns = [
            '/wp-admin/',
            '/wp-login',
            '/wp-content/',
            '/feed/',
            '/comment',
            '/tag/',
            '/category/',
            'mailto:',
            '#',
            '?'
        ]
        
        for pattern in skip_patterns:
            if pattern in url.lower():
                return False
        
        return True
    
    def close(self):
        """Close the session and cleanup resources."""
        if self.session:
            self.session.close()
        
        if self.logger:
            self.logger.info("Scraper session closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()