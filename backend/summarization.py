import traceback
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
import random
from urllib.parse import urlparse
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Summarizer:
    """Handles text summarization and related functionality."""
    
    def __init__(self, advanced_features: bool = False):
        """
        Initialize the Summarizer.
        
        Args:
            advanced_features: Whether advanced NLP features are available
        """
        self.advanced_features = advanced_features
        self.summary_prompt = None
        
        # Common headers to simulate a real browser
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0'
        }
        
        if self.advanced_features:
            self._initialize_advanced_features()
    
    def _initialize_advanced_features(self):
        """Initialize advanced NLP features if available."""
        try:
            from haystack.nodes import PromptNode, PromptTemplate
            
            self.summary_prompt = PromptNode(
                model_name_or_path="google/flan-t5-large",
                default_prompt_template=PromptTemplate(
                    "Summarize the following document: {documents}"
                )
            )
        except Exception as e:
            logger.error(f"Error initializing summarizer advanced features: {str(e)}")
            traceback.print_exc()
            self.advanced_features = False
    
    def summarize(self, content: str) -> str:
        """
        Generate a summary of the provided text.
        
        Args:
            content: Text content to summarize
            
        Returns:
            Summary text
        """
        if not content:
            return "No content provided to summarize."
            
        # Use advanced features if available
        if self.advanced_features and self.summary_prompt:
            try:
                result = self.summary_prompt(documents=[{"content": content}])
                if isinstance(result, dict) and "results" in result:
                    return result["results"][0]
            except Exception as e:
                logger.error(f"Error using summary prompt: {str(e)}")
        
        # Fallback simple summarization
        sentences = content.split('. ')
        if len(sentences) <= 3:
            return content
            
        # Simple summary with first and last sentences
        summary = '. '.join([sentences[0], sentences[1]])
        if len(sentences) > 3:
            summary += '. ' + sentences[-2] + '. ' + sentences[-1]
        return summary
    
    def fetch_webpage_content(self, url: str) -> str:
        """
        Fetch and extract text content from a webpage.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Extracted text content
        """
        logger.info(f"Attempting to fetch content from URL: {url}")
        
        # Ensure URL has a scheme
        if not url.startswith(('http://', 'https://')):
            url = 'https://' + url
            logger.info(f"Added https scheme to URL: {url}")
        
        # Parse the URL to get the domain
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        
        try:
            # Add a small delay to avoid rate limiting
            time.sleep(random.uniform(0.5, 1.5))
            
            # Make the request with headers
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            # Extract the text content using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            
            # Remove unwanted elements
            for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
                tag.decompose()
            
            # Try multiple strategies to extract content
            content = self._extract_content(soup, domain)
            
            # Clean up the extracted content
            content = self._clean_content(content)
            
            if not content or content == "No readable content found.":
                logger.warning(f"Could not extract content from {url}")
                return "No readable content found."
                
            logger.info(f"Successfully extracted {len(content)} characters from {url}")
            return content
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error fetching webpage: {e}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error processing webpage: {e}"
            logger.error(error_msg)
            traceback.print_exc()
            return error_msg
    
    def _extract_content(self, soup, domain: str) -> str:
        """
        Extract content from a webpage using multiple strategies.
        
        Args:
            soup: BeautifulSoup object
            domain: Website domain
            
        Returns:
            Extracted text content
        """
        content = ""
        
        # Strategy 1: Look for main content containers
        main_content = soup.find('main') or soup.find('article') or soup.find(id='content') or soup.find(class_='content')
        if main_content:
            paragraphs = main_content.find_all('p')
            if paragraphs:
                content = "\n\n".join([p.get_text().strip() for p in paragraphs])
        
        # Strategy 2: If no content found, gather all paragraphs
        if not content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                content = "\n\n".join([p.get_text().strip() for p in paragraphs])
        
        # Strategy 3: If still no content, try looking for divs with text
        if not content:
            text_divs = [div for div in soup.find_all('div') if len(div.get_text().strip()) > 100]
            if text_divs:
                content = "\n\n".join([div.get_text().strip() for div in text_divs])
        
        # Strategy 4: Domain-specific extraction for common websites
        if not content and domain:
            content = self._domain_specific_extraction(soup, domain)
        
        # If all strategies fail, get all text
        if not content:
            content = soup.get_text(separator="\n\n").strip()
        
        return content if content else "No readable content found."
    
    def _domain_specific_extraction(self, soup, domain: str) -> str:
        """
        Apply domain-specific content extraction for common websites.
        
        Args:
            soup: BeautifulSoup object
            domain: Website domain
            
        Returns:
            Extracted text content
        """
        # Wikipedia
        if "wikipedia.org" in domain:
            content_div = soup.find('div', {'id': 'mw-content-text'})
            if content_div:
                paragraphs = content_div.find_all('p')
                return "\n\n".join([p.get_text().strip() for p in paragraphs])
        
        # Medium
        if "medium.com" in domain:
            article = soup.find('article')
            if article:
                paragraphs = article.find_all('p')
                return "\n\n".join([p.get_text().strip() for p in paragraphs])
        
        # News websites often use article tags
        article = soup.find('article')
        if article:
            paragraphs = article.find_all('p')
            if paragraphs:
                return "\n\n".join([p.get_text().strip() for p in paragraphs])
        
        return ""
    
    def _clean_content(self, content: str) -> str:
        """
        Clean extracted content.
        
        Args:
            content: Raw extracted content
            
        Returns:
            Cleaned text content
        """
        if not content:
            return content
            
        # Replace multiple newlines with two newlines
        import re
        content = re.sub(r'\n{3,}', '\n\n', content)
        
        # Replace multiple spaces with a single space
        content = re.sub(r' {2,}', ' ', content)
        
        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in content.split('\n')]
        content = '\n'.join(lines)
        
        return content
    
    def save_summary(self, original_content: str, summary: str, title: str = "") -> bool:
        """
        Save a summary for later reference.
        
        Args:
            original_content: The original content
            summary: The generated summary
            title: Optional title for the summary
            
        Returns:
            True if save was successful, False otherwise
        """
        # This would save to a database in a real implementation
        # For now, we'll just return True
        return True
    
    def get_saved_summaries(self) -> List[Dict[str, Any]]:
        """
        Get a list of saved summaries.
        
        Returns:
            List of summaries
        """
        # This would retrieve from a database in a real implementation
        return []