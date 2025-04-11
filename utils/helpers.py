import re
import json
import os
from typing import List, Dict, Any, Union

def is_valid_url(url: str) -> bool:
    url_pattern = re.compile(
        r'^(https?:\/\/)?' 
        r'(www\.)?' 
        r'([a-zA-Z0-9-]+\.)+'
        r'[a-zA-Z]{2,}'
        r'(\/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?' 
        r'$'
    )
    return bool(url_pattern.match(url))

def extract_youtube_id(url: str) -> Union[str, None]:
    youtube_regex = r'(?:youtube\.com\/(?:[^\/\n\s]+\/\S+\/|(?:v|e(?:mbed)?)\/|\S*?[?&]v=)|youtu\.be\/)([a-zA-Z0-9_-]{11})'
    match = re.search(youtube_regex, url)
    return match.group(1) if match else None

def save_to_json(data: Any, filename: str) -> bool:
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception:
        return False

def load_from_json(filename: str) -> Union[Dict, List, None]:
    if not os.path.exists(filename):
        return None
        
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except Exception:
        return None

def clean_text(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def format_file_size(size_bytes: int) -> str:
    if size_bytes < 1024:
        return f"{size_bytes} bytes"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"