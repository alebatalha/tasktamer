from haystack.nodes import PromptNode, PromptTemplate
from typing import List, Dict, Any, Union
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
from config import LLM_MODEL
from backend.core import tamer
import googleapiclient.discovery
import googleapiclient.errors

summary_prompt = PromptNode(
    model_name_or_path=LLM_MODEL,
    default_prompt_template=PromptTemplate(
        "Summarize the following document: {documents}"
    )
)

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

def get_youtube_captions(youtube_url: str) -> str:
    try:
        video_id = extract_youtube_id(youtube_url)
        if not video_id:
            return "Invalid YouTube URL"
            
        api_service_name = "youtube"
        api_version = "v3"
        DEVELOPER_KEY = ""  # Add your YouTube API key here
        
        if not DEVELOPER_KEY:
            return "YouTube API key not configured"
            
        youtube = googleapiclient.discovery.build(
            api_service_name, api_version, developerKey=DEVELOPER_KEY)
            
        request = youtube.captions().list(
            part="snippet",
            videoId=video_id
        )
        response = request.execute()
        
        if "items" in response and response["items"]:
            caption_id = response["items"][0]["id"]
            request = youtube.captions().download(
                id=caption_id,
                tfmt="srt"
            )
            caption_text = request.execute()
            
            clean_text = re.sub(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', '', caption_text)
            clean_text = re.sub(r'^\d+$', '', clean_text, flags=re.MULTILINE)
            return clean_text.strip()
        else:
            return "No captions available for this video"
    except Exception as e:
        return f"Error retrieving YouTube captions: {e}"

def extract_youtube_id(url: str) -> Union[str, None]:
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

def process_url(url: str) -> str:
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.lower()
    
    if 'youtube.com' in domain or 'youtu.be' in domain:
        return get_youtube_captions(url)
    else:
        return fetch_webpage_content(url)

def summarize_content(content: str = None, url: str = None) -> str:
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
    return "Failed to generate summary."