"""
Text summarization functionality for TaskTamer.
"""
import traceback
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any

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
            print(f"Error initializing summarizer advanced features: {str(e)}")
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
                print(f"Error using summary prompt: {str(e)}")
        
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
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join([p.get_text() for p in paragraphs])
            return text if text else "No readable content found."
        except requests.RequestException as e:
            return f"Error fetching webpage: {e}"
    
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