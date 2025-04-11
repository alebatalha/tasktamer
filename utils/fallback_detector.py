USING_FALLBACK = False

def haystack_available():
    try:
        import haystack
        return True
    except ImportError:
        return False

HAYSTACK_AVAILABLE = haystack_available()
USING_FALLBACK = not HAYSTACK_AVAILABLE

def check_dependencies():
    return {
        "haystack": HAYSTACK_AVAILABLE,
        "fallback_mode": USING_FALLBACK
    }