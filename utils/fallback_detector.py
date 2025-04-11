def haystack_available():
    try:
        import haystack
        return True
    except ImportError:
        return False

def youtube_api_available():
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        return True
    except ImportError:
        return False

# Set flags at module import time
HAYSTACK_AVAILABLE = haystack_available()
YOUTUBE_API_AVAILABLE = youtube_api_available()
USING_FALLBACK = not HAYSTACK_AVAILABLE

def check_dependencies():
    """Return a dictionary of available dependencies."""
    return {
        "haystack": HAYSTACK_AVAILABLE,
        "youtube_api": YOUTUBE_API_AVAILABLE,
        "fallback_mode": USING_FALLBACK
    }