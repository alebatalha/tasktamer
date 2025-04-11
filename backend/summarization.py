# backend/summarization.py
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

def summarize_documents(text):
    """Creates a simple summary of text without using external AI libraries.
    This is a placeholder that extracts important sentences from the document."""
    if not text or len(text.strip()) < 50:
        return "The provided content is too short to summarize. Please provide more text."
    
    # Simple extractive summarization approach
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return "Could not extract valid sentences for summarization."
    
    # Score sentences based on simple heuristics
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        
        # Position score - earlier sentences often contain important information
        position_score = a = 1.0 if i < 3 else 0.5 if i < 5 else 0.3
        score += position_score
        
        # Length score - not too short, not too long
        words = sentence.split()
        length_score = 0.5 if 5 <= len(words) <= 25 else 0.2
        score += length_score
        
        # Keyword score - contains important-sounding words
        important_keywords = ["important", "significant", "key", "main", "critical", "essential", "primary", "major", "crucial"]
        keyword_score = sum(1 for word in words if word.lower() in important_keywords) * 0.5
        score += keyword_score
        
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True)
    
    # Determine number of sentences to include in summary (roughly 20-30% of original)
    summary_size = max(3, min(int(len(sentences) * 0.3), 10))
    
    # Get top sentences and sort them by original order
    top_sentences = [s[1] for s in scored_sentences[:summary_size]]
    ordered_sentences = []
    for sentence in sentences:
        if sentence in top_sentences:
            ordered_sentences.append(sentence)
            if len(ordered_sentences) >= summary_size:
                break
    
    # Combine into a summary
    summary = " ".join(ordered_sentences)
    
    # Add a disclaimer
    disclaimer = "\n\n(Note: This is a basic extractive summary. For better results, TaskTamer would use AI-based summarization in a production environment.)"
    
    return summary + disclaimer

def fetch_webpage_content(url):
    """Fetches and extracts text content from a web page."""
    try:
        # Check if it's a YouTube URL
        if is_youtube_url(url):
            return fetch_youtube_captions(url)
            
        # Otherwise treat it as a regular webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        
        # Get text content from paragraphs, headings, and lists
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = "\n".join([elem.get_text().strip() for elem in paragraphs if elem.get_text().strip()])
        
        if not text:
            # If no structured elements found, get all text
            text = soup.get_text()
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
        
        return text if text else "No readable content found."
    except requests.RequestException as e:
        return f"Error fetching webpage: {str(e)}"
    except Exception as e:
        return f"Error processing webpage: {str(e)}"

def is_youtube_url(url):
    """Check if a URL is a YouTube video."""
    parsed_url = urlparse(url)
    
    # Standard YouTube URLs
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com') and parsed_url.path == '/watch':
        return True
    
    # YouTube Shorts
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com') and '/shorts/' in parsed_url.path:
        return True
    
    # Shortened youtu.be links
    if parsed_url.netloc == 'youtu.be':
        return True
    
    return False

def fetch_youtube_captions(url):
    """
    Attempt to fetch captions/transcripts from a YouTube video.
    
    This is a simplified version. In a production app, you would:
    1. Use the YouTube Data API
    2. Or use a library like youtube-transcript-api
    
    This function simulates getting transcripts by returning a placeholder message
    """
    try:
        # Extract video ID
        video_id = None
        parsed_url = urlparse(url)
        
        if parsed_url.netloc in ('youtube.com', 'www.youtube.com'):
            if parsed_url.path == '/watch':
                # Regular YouTube URL
                query = parse_qs(parsed_url.query)
                video_id = query.get('v', [''])[0]
            elif '/shorts/' in parsed_url.path:
                # YouTube Shorts
                video_id = parsed_url.path.split('/shorts/')[1]
        elif parsed_url.netloc == 'youtu.be':
            # Shortened URL
            video_id = parsed_url.path.lstrip('/')
        
        if not video_id:
            return "Could not extract YouTube video ID from URL."
        
        # In a real implementation, you would call YouTube API or use youtube-transcript-api here
        # For this demo, we'll return a placeholder explaining what we would do
        
        return f"""
This is a placeholder for YouTube video transcript content from video ID: {video_id}

In a full implementation, TaskTamer would:
1. Use the YouTube Data API or a library like youtube-transcript-api to fetch actual captions
2. Process closed captions or auto-generated transcripts if available
3. Provide a complete transcript of the video content

The summary would then be generated based on the actual transcript content.

For demonstration purposes, let's assume this is the transcript of an educational video about task management strategies:

Task management is essential for productivity. Breaking complex tasks into smaller steps helps make them more manageable. The Pomodoro Technique suggests working in focused intervals of 25 minutes followed by short breaks. Another effective strategy is time blocking, where you schedule specific activities during designated time slots. Prioritization is also crucial - the Eisenhower Matrix helps categorize tasks by urgency and importance. Regular reviews of your task list help ensure you're on track and making progress toward your goals. Digital tools can enhance task management by providing reminders, organization features, and synchronization across devices.
"""
    except Exception as e:
        return f"Error processing YouTube video: {str(e)}"