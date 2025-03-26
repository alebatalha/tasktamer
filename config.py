"""
Configuration settings for TaskTamer application.
"""

# Application settings
APP_NAME = "TaskTamer"
APP_VERSION = "1.0.0"
APP_ICON = "🧙‍♂️"
APP_THEME = {
    "primary_color": "#4a154b",  # Purple
    "secondary_color": "#28a745",  # Green
    "background_color": "#f8f9fa",  # Light gray
    "text_color": "#333333"  # Dark gray
}

# Feature configuration
FEATURES = {
    "task_breakdown": {
        "name": "Task Breaker",
        "icon": "📋",
        "description": "Break complex tasks into manageable steps",
        "enabled": True
    },
    "summarizer": {
        "name": "Summarizer",
        "icon": "📝",
        "description": "Generate concise summaries of your documents",
        "enabled": True
    },
    "quiz": {
        "name": "Quiz Master",
        "icon": "🧠",
        "description": "Create quizzes to test your knowledge",
        "enabled": True
    }
}

# File handling
TEMP_DIR = "temp"
SUPPORTED_FILE_TYPES = ["txt", "pdf"]
MAX_FILE_SIZE_MB = 5

# Advanced options
ENABLE_DEBUGGING = False
LOG_LEVEL = "INFO"