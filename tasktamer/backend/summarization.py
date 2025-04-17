from typing import List, Dict, Any, Union
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from utils.fallback_detector import HAYSTACK_AVAILABLE
from backend.core import tamer

def fetch_webpage_content(url: str) -> str:
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
            
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        if not text:
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                text = main_content.get_text(separator="\n", strip=True)
            
        return text if text else "No readable content found."
    except requests.RequestException as e:
        return f"Error fetching webpage: {e}"

def process_url(url: str) -> str:
    return fetch_webpage_content(url)

def simple_summarize(content: str) -> str:
    if not content:
        return "No content provided for summarization."
            
    sentences = re.split(r'(?<=[.!?])\s+', content)
        
    if len(sentences) <= 3:
        return content
            
    summary_sentences = [
        sentences[0],
        sentences[len(sentences) // 2],
        sentences[-1]
    ]
        
    return " ".join(summary_sentences)

if HAYSTACK_AVAILABLE:
    try:
        from haystack.nodes import PromptNode, PromptTemplate
        from config import LLM_MODEL
        
        summary_prompt = PromptNode(
            model_name_or_path=LLM_MODEL,
            default_prompt_template=PromptTemplate(
                "Summarize the following document: {documents}"
            )
        )
        
        def summarize_content(content: str = None, url: str = None) -> str:
            try:
                if url:
                    content = process_url(url)
                
                if not content:
                    return "No content provided for summarization."
                    
                processed_docs = tamer.process_text(content)
                if not processed_docs:
                    return "Failed to process the content."
                    
                summary = summary_prompt(documents=processed_docs)
                
                if isinstance(summary, dict) and "results" in summary:
                    return summary["results"][0]
                return simple_summarize(content)
            except Exception:
                return simple_summarize(content)
    except Exception:
        def summarize_content(content: str = None, url: str = None) -> str:
            if url:
                content = process_url(url)
            return simple_summarize(content)
else:
    def summarize_content(content: str = None, url: str = None) -> str:
        if url:
            content = process_url(url)
        return simple_summarize(content)