"""Data export utilities for scraper-classicist-org."""

import json
import csv
import pandas as pd
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class DataExporter:
    """Utility class for exporting scraped data to various formats."""
    
    def __init__(self, output_dir: Path, logger=None):
        """Initialize the data exporter.
        
        Args:
            output_dir: Directory to save exported files
            logger: Logger instance
        """
        self.output_dir = Path(output_dir)
        self.logger = logger
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export(self, data: Dict[str, Any], 
               format: str = "json", 
               output_file: Optional[Path] = None) -> Path:
        """Export data to the specified format.
        
        Args:
            data: Data to export
            format: Export format ('json', 'csv', 'excel')
            output_file: Optional output file path
            
        Returns:
            Path to the exported file
        """
        if format == "json":
            return self._export_json(data, output_file)
        elif format == "csv":
            return self._export_csv(data, output_file)
        elif format == "excel":
            return self._export_excel(data, output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_json(self, data: Dict[str, Any], 
                     output_file: Optional[Path] = None) -> Path:
        """Export data as JSON.
        
        Args:
            data: Data to export
            output_file: Optional output file path
            
        Returns:
            Path to the exported JSON file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"scraped_data_{timestamp}.json"
        
        # Prepare data for JSON export
        json_data = self._prepare_for_json(data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False, default=str)
        
        if self.logger:
            self.logger.info(f"Data exported to JSON: {output_file}")
        
        return output_file
    
    def _export_csv(self, data: Dict[str, Any], 
                    output_file: Optional[Path] = None) -> Path:
        """Export data as CSV.
        
        Args:
            data: Data to export
            output_file: Optional output file path
            
        Returns:
            Path to the exported CSV file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"scraped_data_{timestamp}.csv"
        
        # Flatten data for CSV export
        csv_data = self._flatten_for_csv(data)
        
        if not csv_data:
            # Create a simple CSV with basic info
            csv_data = [{
                'url': data.get('url', ''),
                'timestamp': data.get('timestamp', ''),
                'title': '',
                'content': '',
                'page_type': '',
                'authors': '',
                'keywords': ''
            }]
        
        # Write to CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            if csv_data:
                fieldnames = csv_data[0].keys()
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(csv_data)
        
        if self.logger:
            self.logger.info(f"Data exported to CSV: {output_file}")
        
        return output_file
    
    def _export_excel(self, data: Dict[str, Any], 
                      output_file: Optional[Path] = None) -> Path:
        """Export data as Excel file.
        
        Args:
            data: Data to export
            output_file: Optional output file path
            
        Returns:
            Path to the exported Excel file
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.output_dir / f"scraped_data_{timestamp}.xlsx"
        
        # Flatten data for Excel export
        excel_data = self._flatten_for_csv(data)
        
        if not excel_data:
            excel_data = [{
                'url': data.get('url', ''),
                'timestamp': data.get('timestamp', ''),
                'title': '',
                'content': '',
                'page_type': '',
                'authors': '',
                'keywords': ''
            }]
        
        # Create DataFrame and export to Excel
        df = pd.DataFrame(excel_data)
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Scraped Data', index=False)
            
            # Add metadata sheet if available
            if 'metadata' in data:
                metadata_df = pd.DataFrame([data['metadata']])
                metadata_df.to_excel(writer, sheet_name='Metadata', index=False)
        
        if self.logger:
            self.logger.info(f"Data exported to Excel: {output_file}")
        
        return output_file
    
    def _prepare_for_json(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare data for JSON export.
        
        Args:
            data: Raw data
            
        Returns:
            Data prepared for JSON export
        """
        json_data = {
            'export_info': {
                'timestamp': datetime.now().isoformat(),
                'source': data.get('url', ''),
                'tool': 'scraper-classicist-org'
            },
            'scraping_info': {
                'depth': data.get('depth', 1),
                'pages_found': len(data.get('data', [])),
                'errors': data.get('errors', [])
            },
            'pages': []
        }
        
        # Process each page
        for page in data.get('data', []):
            page_data = {
                'url': page.get('url', ''),
                'title': page.get('title', ''),
                'status_code': page.get('status_code', ''),
                'content_type': page.get('content_type', ''),
                'metadata': page.get('metadata', {}),
                'extracted_data': page.get('extracted_data', {}),
                'links_count': len(page.get('links', [])),
                'content_preview': self._get_content_preview(page.get('content', '')),
                'authors': page.get('extracted_data', {}).get('authors', []),
                'keywords': page.get('extracted_data', {}).get('keywords', [])
            }
            json_data['pages'].append(page_data)
        
        return json_data
    
    def _flatten_for_csv(self, data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Flatten data for CSV export.
        
        Args:
            data: Raw data
            
        Returns:
            List of flattened dictionaries
        """
        flattened = []
        
        for page in data.get('data', []):
            extracted = page.get('extracted_data', {})
            
            flat_row = {
                'url': page.get('url', ''),
                'timestamp': data.get('timestamp', ''),
                'title': page.get('title', ''),
                'status_code': page.get('status_code', ''),
                'content_type': page.get('content_type', ''),
                'page_type': extracted.get('page_type', ''),
                'authors': '; '.join([a.get('name', '') for a in extracted.get('authors', [])]),
                'keywords': '; '.join(extracted.get('keywords', [])),
                'content_length': len(page.get('content', '')),
                'content_preview': self._get_content_preview(page.get('content', '')),
                'links_count': len(page.get('links', [])),
                'issue_number': extracted.get('issue_number', ''),
                'year': extracted.get('year', ''),
                'abstract': extracted.get('abstract', '')
            }
            
            flattened.append(flat_row)
        
        return flattened
    
    def _get_content_preview(self, content: str, max_length: int = 200) -> str:
        """Get a preview of the content.
        
        Args:
            content: Full content
            max_length: Maximum length of preview
            
        Returns:
            Content preview
        """
        if not content:
            return ''
        
        # Remove extra whitespace
        content = ' '.join(content.split())
        
        if len(content) <= max_length:
            return content
        
        return content[:max_length] + '...'
    
    def export_summary(self, data: Dict[str, Any]) -> Path:
        """Export a summary of the scraping results.
        
        Args:
            data: Scraped data
            
        Returns:
            Path to the summary file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.output_dir / f"summary_{timestamp}.txt"
        
        summary = self._generate_summary(data)
        
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        if self.logger:
            self.logger.info(f"Summary exported: {summary_file}")
        
        return summary_file
    
    def _generate_summary(self, data: Dict[str, Any]) -> str:
        """Generate a text summary of the scraping results.
        
        Args:
            data: Scraped data
            
        Returns:
            Summary text
        """
        summary_lines = []
        summary_lines.append("SCRAPING SUMMARY")
        summary_lines.append("=" * 50)
        summary_lines.append(f"Source URL: {data.get('url', 'Unknown')}")
        summary_lines.append(f"Scraping Depth: {data.get('depth', 1)}")
        summary_lines.append(f"Timestamp: {datetime.fromtimestamp(data.get('timestamp', 0)).isoformat()}")
        summary_lines.append("")
        
        pages = data.get('data', [])
        summary_lines.append(f"Pages Scraped: {len(pages)}")
        summary_lines.append(f"Errors: {len(data.get('errors', []))}")
        summary_lines.append("")
        
        if pages:
            summary_lines.append("PAGE DETAILS:")
            summary_lines.append("-" * 30)
            
            for i, page in enumerate(pages, 1):
                extracted = page.get('extracted_data', {})
                summary_lines.append(f"{i}. {page.get('title', 'No title')}")
                summary_lines.append(f"   URL: {page.get('url', 'No URL')}")
                summary_lines.append(f"   Type: {extracted.get('page_type', 'Unknown')}")
                summary_lines.append(f"   Status: {page.get('status_code', 'N/A')}")
                summary_lines.append(f"   Content Length: {len(page.get('content', ''))}")
                
                authors = extracted.get('authors', [])
                if authors:
                    author_names = [a.get('name', '') for a in authors[:3]]  # Limit to first 3
                    summary_lines.append(f"   Authors: {', '.join(author_names)}")
                
                summary_lines.append("")
        
        if data.get('errors'):
            summary_lines.append("ERRORS:")
            summary_lines.append("-" * 30)
            for error in data.get('errors', []):
                summary_lines.append(f"- {error}")
            summary_lines.append("")
        
        summary_lines.append("=" * 50)
        summary_lines.append(f"Generated by scraper-classicist-org on {datetime.now().isoformat()}")
        
        return '\n'.join(summary_lines)