#!/usr/bin/env python3
"""
Belastingdienst APA PDF Crawler
Crawls the Dutch tax authority's APA rulings page to extract PDF download links.
"""

import requests
from bs4 import BeautifulSoup
import re
import time
import json
import os
from urllib.parse import urljoin, urlparse
import logging
from typing import List, Dict, Set
from dataclasses import dataclass
from datetime import datetime

@dataclass
class APADocument:
    title: str
    intermediate_url: str
    pdf_url: str
    date_found: str

class APACrawler:
    def __init__(self, base_url: str, delay: float = 1.0):
        self.base_url = base_url
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.found_documents: List[APADocument] = []
        self.processed_urls: Set[str] = set()
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('apa_crawler.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_page(self, url: str) -> BeautifulSoup:
        """Fetch a page and return BeautifulSoup object."""
        try:
            self.logger.info(f"Fetching: {url}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except requests.RequestException as e:
            self.logger.error(f"Error fetching {url}: {e}")
            return None

    def extract_apa_links(self, soup: BeautifulSoup, base_url: str) -> List[str]:
        """Extract APA ruling links from the main page."""
        links = []
        
        # Look for links that contain APA-related content
        # These might be in various formats, so we'll be flexible
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if not href:
                continue
                
            # Convert relative URLs to absolute
            full_url = urljoin(base_url, href)
            
            # Look for patterns that suggest APA rulings
            if any(pattern in href.lower() for pattern in [
                'advance-pricing-agreement',
                'apa-',
                '/rul-',
                'ruling'
            ]):
                links.append(full_url)
                continue
            
            # Also check link text for APA references
            link_text = link.get_text(strip=True).lower()
            if any(pattern in link_text for pattern in [
                'apa',
                'advance pricing agreement',
                'ruling'
            ]):
                links.append(full_url)
        
        return list(set(links))  # Remove duplicates

    def find_pdf_link(self, soup: BeautifulSoup, page_url: str) -> str:
        """Find PDF download link on an intermediate page."""
        # Method 1: Look for direct PDF links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and href.lower().endswith('.pdf'):
                return urljoin(page_url, href)
        
        # Method 2: Look for download.belastingdienst.nl links
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            if href and 'download.belastingdienst.nl' in href:
                return href
        
        # Method 3: Look for links with download-related text
        for link in soup.find_all('a', href=True):
            link_text = link.get_text(strip=True).lower()
            if any(word in link_text for word in ['download', 'pdf', 'document']):
                href = link.get('href')
                if href:
                    full_url = urljoin(page_url, href)
                    # Check if this leads to a PDF
                    if self.is_pdf_url(full_url):
                        return full_url
        
        # Method 4: Look in meta tags or script tags for PDF references
        for meta in soup.find_all('meta'):
            content = meta.get('content', '')
            if content and '.pdf' in content:
                potential_url = self.extract_url_from_text(content)
                if potential_url:
                    return urljoin(page_url, potential_url)
        
        return None

    def is_pdf_url(self, url: str) -> bool:
        """Check if URL likely points to a PDF."""
        return url.lower().endswith('.pdf') or 'download.belastingdienst.nl' in url

    def extract_url_from_text(self, text: str) -> str:
        """Extract URL from text using regex."""
        url_pattern = r'https?://[^\s<>"]+\.pdf'
        match = re.search(url_pattern, text)
        return match.group(0) if match else None

    def extract_title(self, soup: BeautifulSoup) -> str:
        """Extract document title from page."""
        # Try different title extraction methods
        title_selectors = [
            'h1',
            'title',
            '.page-title',
            '.document-title',
            '[class*="title"]'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = element.get_text(strip=True)
                if title and len(title) > 5:  # Reasonable title length
                    return title
        
        return "Unknown Document"

    def crawl_apa_page(self, url: str) -> APADocument:
        """Crawl a single APA page to find PDF."""
        if url in self.processed_urls:
            return None
        
        self.processed_urls.add(url)
        
        soup = self.fetch_page(url)
        if not soup:
            return None
        
        # Extract title
        title = self.extract_title(soup)
        
        # Find PDF link
        pdf_url = self.find_pdf_link(soup, url)
        
        if pdf_url:
            document = APADocument(
                title=title,
                intermediate_url=url,
                pdf_url=pdf_url,
                date_found=datetime.now().isoformat()
            )
            self.logger.info(f"Found PDF: {title} -> {pdf_url}")
            return document
        else:
            self.logger.warning(f"No PDF found on {url}")
            return None

    def crawl_main_page(self) -> List[APADocument]:
        """Crawl the main APA page and extract all PDF documents."""
        self.logger.info("Starting APA crawl...")
        
        # Fetch main page
        soup = self.fetch_page(self.base_url)
        if not soup:
            self.logger.error("Failed to fetch main page")
            return []
        
        # Extract APA links
        apa_links = self.extract_apa_links(soup, self.base_url)
        self.logger.info(f"Found {len(apa_links)} potential APA links")
        
        # Process each link
        for link in apa_links:
            time.sleep(self.delay)  # Be respectful
            
            document = self.crawl_apa_page(link)
            if document:
                self.found_documents.append(document)
        
        self.logger.info(f"Crawl complete. Found {len(self.found_documents)} PDF documents")
        return self.found_documents

    def save_results(self, filename: str = "apa_documents.json"):
        """Save results to JSON file."""
        data = {
            'crawl_date': datetime.now().isoformat(),
            'base_url': self.base_url,
            'total_documents': len(self.found_documents),
            'documents': [
                {
                    'title': doc.title,
                    'intermediate_url': doc.intermediate_url,
                    'pdf_url': doc.pdf_url,
                    'date_found': doc.date_found
                }
                for doc in self.found_documents
            ]
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Results saved to {filename}")

    def download_pdfs(self, download_dir: str = "pdfs"):
        """Download all found PDFs."""
        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
        
        for doc in self.found_documents:
            try:
                self.logger.info(f"Downloading: {doc.pdf_url}")
                response = self.session.get(doc.pdf_url, timeout=60)
                response.raise_for_status()
                
                # Generate filename
                filename = os.path.basename(urlparse(doc.pdf_url).path)
                if not filename or not filename.endswith('.pdf'):
                    filename = f"apa_document_{len(os.listdir(download_dir)) + 1}.pdf"
                
                filepath = os.path.join(download_dir, filename)
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                self.logger.info(f"Downloaded: {filepath}")
                time.sleep(self.delay)
                
            except Exception as e:
                self.logger.error(f"Error downloading {doc.pdf_url}: {e}")

def main():
    """Main function to run the crawler."""
    base_url = "https://www.belastingdienst.nl/wps/wcm/connect/bldcontentnl/standaard_functies/prive/contact/rechten_en_plichten_bij_de_belastingdienst/ruling/apa"
    
    crawler = APACrawler(base_url, delay=1.0)
    
    # Crawl for documents
    documents = crawler.crawl_main_page()
    
    # Save results
    crawler.save_results()
    
    # Print summary
    print(f"\n=== Crawl Summary ===")
    print(f"Total documents found: {len(documents)}")
    print(f"Results saved to: apa_documents.json")
    print(f"Log file: apa_crawler.log")
    
    if documents:
        print(f"\nFound PDFs:")
        for i, doc in enumerate(documents, 1):
            print(f"{i}. {doc.title}")
            print(f"   PDF: {doc.pdf_url}")
            print()
        
        # Ask if user wants to download
        download = input("Download all PDFs? (y/n): ").lower().strip()
        if download == 'y':
            crawler.download_pdfs()
            print("Download complete!")

if __name__ == "__main__":
    main()