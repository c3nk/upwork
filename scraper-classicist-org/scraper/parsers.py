"""HTML parsing and data extraction utilities for classicist.org."""

import re
from typing import Dict, List, Any, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup, Tag


class HTMLParser:
    """Utility class for parsing HTML content."""
    
    def __init__(self):
        """Initialize the HTML parser."""
        # Common selectors for content extraction
        self.content_selectors = [
            'main',
            'article',
            '.post-content',
            '.entry-content', 
            '.content',
            '#content',
            'div[class*="content"]',
            'div[class*="post"]'
        ]
        
        self.nav_selectors = [
            'nav',
            '.navigation',
            '.menu',
            'ul[class*="nav"]',
            'div[class*="menu"]'
        ]
    
    def extract_main_content(self, soup: BeautifulSoup) -> str:
        """Extract the main content from a page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Main content as text
        """
        # Try each selector until we find content
        for selector in self.content_selectors:
            element = soup.select_one(selector)
            if element:
                # Clean up the content
                for tag in element.find_all(['script', 'style', 'nav', 'footer']):
                    tag.decompose()
                return element.get_text(separator='\n', strip=True)
        
        # Fallback: try to find the largest text block
        return self._extract_largest_text_block(soup)
    
    def _extract_largest_text_block(self, soup: BeautifulSoup) -> str:
        """Extract the largest text block from the page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Largest text block as text
        """
        # Remove script and style elements
        for tag in soup.find_all(['script', 'style']):
            tag.decompose()
        
        # Find all text-containing elements
        elements = []
        for tag in soup.find_all(['p', 'div', 'section', 'article']):
            text = tag.get_text(strip=True)
            if len(text) > 100:  # Only consider substantial text blocks
                elements.append((tag, len(text)))
        
        if not elements:
            return soup.get_text(separator='\n', strip=True)
        
        # Return the largest text block
        largest = max(elements, key=lambda x: x[1])[0]
        return largest.get_text(separator='\n', strip=True)
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from the page.
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Dictionary of metadata
        """
        metadata = {}
        
        # Title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text().strip()
        
        # Meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                metadata[name] = content
        
        # Author
        author_selectors = [
            'meta[name="author"]',
            'meta[property="article:author"]',
            '.author',
            '.byline',
            '[class*="author"]'
        ]
        
        for selector in author_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    metadata['author'] = element.get('content', '').strip()
                else:
                    metadata['author'] = element.get_text().strip()
                break
        
        # Publication date
        date_selectors = [
            'meta[property="article:published_time"]',
            'meta[name="date"]',
            'time[datetime]',
            '.date',
            '.published',
            '[class*="date"]'
        ]
        
        for selector in date_selectors:
            element = soup.select_one(selector)
            if element:
                if element.name == 'meta':
                    metadata['date'] = element.get('content', '').strip()
                else:
                    metadata['date'] = element.get('datetime') or element.get_text().strip()
                break
        
        return metadata
    
    def extract_links(self, soup: BeautifulSoup, base_url: str = "") -> List[Dict[str, str]]:
        """Extract all links from the page.
        
        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links
            
        Returns:
            List of dictionaries with link information
        """
        links = []
        
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            text = a_tag.get_text(strip=True)
            title = a_tag.get('title', '')
            
            # Resolve relative URLs
            if base_url:
                full_url = urljoin(base_url, href)
            else:
                full_url = href
            
            links.append({
                'url': full_url,
                'text': text,
                'title': title
            })
        
        return links


class DataExtractor:
    """Specialized data extractor for classicist.org content."""
    
    def __init__(self):
        """Initialize the data extractor."""
        # Patterns for classicist.org specific content
        self.article_patterns = [
            r'ISSUE\s+\d+',
            r'Volume\s+\d+',
            r'Classical\s+\w+',
            r'Ancient\s+\w+'
        ]
        
        self.author_patterns = [
            r'by\s+([A-Z][a-z]+\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+[A-Z][a-z]+),?\s+Ph\.?D\.?',
            r'Prof\.?\s+([A-Z][a-z]+\s+[A-Z][a-z]+)'
        ]
    
    def extract_data(self, soup: BeautifulSoup, url: str) -> Dict[str, Any]:
        """Extract structured data based on page type.
        
        Args:
            soup: BeautifulSoup object
            url: Page URL
            
        Returns:
            Dictionary of extracted data
        """
        data = {
            'page_type': self._determine_page_type(soup, url),
            'articles': [],
            'issues': [],
            'authors': [],
            'keywords': []
        }
        
        # Extract based on page type
        if data['page_type'] == 'article':
            data.update(self._extract_article_data(soup))
        elif data['page_type'] == 'issue':
            data.update(self._extract_issue_data(soup))
        elif data['page_type'] == 'archive':
            data.update(self._extract_archive_data(soup))
        
        # Extract common elements
        data['keywords'] = self._extract_keywords(soup)
        data['authors'] = self._extract_authors(soup)
        
        return data
    
    def _determine_page_type(self, soup: BeautifulSoup, url: str) -> str:
        """Determine the type of page based on URL and content.
        
        Args:
            soup: BeautifulSoup object
            url: Page URL
            
        Returns:
            Page type string
        """
        url_lower = url.lower()
        
        if '/article/' in url_lower or '/post/' in url_lower:
            return 'article'
        elif '/issue/' in url_lower or '/issues/' in url_lower:
            return 'issue'
        elif '/archive' in url_lower or '/archives/' in url_lower:
            return 'archive'
        elif 'about' in url_lower:
            return 'about'
        else:
            return 'homepage'
    
    def _extract_article_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data from an article page."""
        article_data = {}
        
        # Article title (try different selectors)
        title_selectors = ['h1', '.entry-title', '.post-title', 'title']
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                article_data['title'] = element.get_text().strip()
                break
        
        # Abstract or summary
        abstract_selectors = ['.abstract', '.summary', '.excerpt', '[class*="abstract"]']
        for selector in abstract_selectors:
            element = soup.select_one(selector)
            if element:
                article_data['abstract'] = element.get_text().strip()
                break
        
        # Main content
        parser = HTMLParser()
        article_data['content'] = parser.extract_main_content(soup)
        
        return article_data
    
    def _extract_issue_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data from an issue page."""
        issue_data = {}
        
        # Issue number and date
        issue_selectors = [
            '.issue-title',
            '.issue-number',
            'h1',
            'title'
        ]
        
        for selector in issue_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                # Try to extract issue number
                issue_match = re.search(r'(?:issue|volume)\s+(\d+)', text, re.IGNORECASE)
                if issue_match:
                    issue_data['issue_number'] = issue_match.group(1)
                
                # Try to extract date
                date_match = re.search(r'(\d{4})', text)
                if date_match:
                    issue_data['year'] = date_match.group(1)
                
                issue_data['title'] = text
                break
        
        # Extract articles in this issue
        article_links = soup.find_all('a', href=re.compile(r'/article/|/post/'))
        articles = []
        for link in article_links:
            articles.append({
                'title': link.get_text().strip(),
                'url': link.get('href', '')
            })
        
        issue_data['articles'] = articles
        
        return issue_data
    
    def _extract_archive_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract data from an archive page."""
        archive_data = {}
        
        # Extract issue links
        issue_links = soup.find_all('a', href=re.compile(r'/issue/|/issues/'))
        issues = []
        for link in issue_links:
            title = link.get_text().strip()
            url = link.get('href', '')
            
            # Try to extract issue number and year from title
            issue_match = re.search(r'(?:issue|volume)\s+(\d+)', title, re.IGNORECASE)
            year_match = re.search(r'(\d{4})', title)
            
            issues.append({
                'title': title,
                'url': url,
                'issue_number': issue_match.group(1) if issue_match else None,
                'year': year_match.group(1) if year_match else None
            })
        
        archive_data['issues'] = issues
        
        return archive_data
    
    def _extract_keywords(self, soup: BeautifulSoup) -> List[str]:
        """Extract keywords from the page."""
        keywords = []
        
        # From meta tags
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords:
            content = meta_keywords.get('content', '')
            keywords.extend([k.strip() for k in content.split(',') if k.strip()])
        
        # From content - look for capitalized terms that might be keywords
        content = soup.get_text()
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b', content)
        
        # Filter common words and duplicates
        common_words = {'The', 'And', 'For', 'With', 'That', 'This', 'From', 'Have', 'Not', 'But', 'You'}
        keywords.extend([word for word in words if word not in common_words and len(word) > 3])
        
        # Remove duplicates and limit to reasonable number
        unique_keywords = list(dict.fromkeys(keywords))[:20]
        
        return unique_keywords
    
    def _extract_authors(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract author information from the page."""
        authors = []
        
        # From meta tags
        meta_author = soup.find('meta', attrs={'name': 'author'})
        if meta_author:
            authors.append({
                'name': meta_author.get('content', '').strip(),
                'type': 'meta'
            })
        
        # From content patterns
        content = soup.get_text()
        for pattern in self.author_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                authors.append({
                    'name': match.strip(),
                    'type': 'extracted'
                })
        
        # Remove duplicates
        unique_authors = []
        seen = set()
        for author in authors:
            if author['name'].lower() not in seen:
                seen.add(author['name'].lower())
                unique_authors.append(author)
        
        return unique_authors