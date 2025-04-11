"""Utils package for TaskTamer."""
import requests
import re
from .helpers import ensure_directories, handle_file_upload, clear_session_state
from typing import Union

__all__ = [
    'ensure_directories',
    'handle_file_upload',
    'clear_session_state',
    'extract_youtube_id',
    'get_youtube_captions'
]

def extract_youtube_id(url: str) -> Union[str, None]:
    """Extracts YouTube video ID from a URL."""
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

def get_youtube_captions(youtube_url: str, api_key: str = None) -> str:
    """Fetches captions/subtitles from a YouTube video.
   
    Args:
        youtube_url: The URL of the YouTube video
        api_key: Your YouTube Data API key
       
    Returns:
        The caption text or an error message
    """
    try:
        video_id = extract_youtube_id(youtube_url)
        if not video_id:
            return "Invalid YouTube URL"
           
        if not api_key:
            return "YouTube API key not provided. Please add your API key in config.py"
           

        captions_url = f"https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={video_id}&key={api_key}"
        response = requests.get(captions_url)
        response.raise_for_status()
        captions_data = response.json()
       
        if "items" not in captions_data or not captions_data["items"]:
            return "No captions available for this video"
           
        caption_id = captions_data["items"][0]["id"]
       

        download_url = f"https://www.googleapis.com/youtube/v3/captions/{caption_id}?key={api_key}"
        headers = {"Accept": "application/json"}
       
        response = requests.get(download_url, headers=headers)
        response.raise_for_status()
       

        caption_text = response.text
     
        clean_text = re.sub(r'\d+:\d+:\d+,\d+ --> \d+:\d+:\d+,\d+', '', caption_text)
        clean_text = re.sub(r'^\d+$', '', clean_text, flags=re.MULTILINE)
       
        return clean_text.strip()
    except requests.RequestException as e:
        return f"Error retrieving YouTube captions: {e}"
    except Exception as e:
        return f"An error occurred: {str(e)}"