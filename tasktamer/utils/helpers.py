import re
import json
import os
import streamlit as st
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

def ensure_directories(*dirs):
    for directory in dirs:
        os.makedirs(directory, exist_ok=True)
    return True

def handle_file_upload(uploaded_file):
    if uploaded_file is None:
        return None
        
    try:
        content = uploaded_file.getvalue().decode("utf-8")
        return content
    except UnicodeDecodeError:
        return uploaded_file.getvalue()

def clear_session_state(*keys):
    for key in keys:
        if key in st.session_state:
            del st.session_state[key]