def haystack_available():
    """Check if Haystack is available."""
    try:
        import haystack
        return True
    except ImportError:
        return False

# Set this once at import time
USING_FALLBACK = not haystack_available()