"""
TaskTamer - Your magical productivity assistant.
Main application entry point.
"""
import streamlit as st

# This MUST be the first Streamlit command
st.set_page_config(
    page_title="TaskTamer",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Now import everything else
import os
import sys
from pathlib import Path

# Ensure directories exist in path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import backend, UI components, and utilities
try:
    from backend.core import TaskTamer
    from ui.styles import apply_custom_css
    from ui.pages.home_page import show_home_page
    from ui.pages.task_page import show_task_page
    from ui.pages.summary_page import show_summary_page
    from ui.pages.quiz_page import show_quiz_page
    from ui.pages.chat_component import show_chat_component
    from utils.helpers import ensure_directories
except ImportError as e:
    st.error(f"Could not import required modules: {str(e)}")
    st.info("Make sure all required directories and modules exist.")
    st.stop()

# Initialize environment
ensure_directories()

# Initialize TaskTamer
@st.cache_resource
def get_task_tamer():
    return TaskTamer()

task_tamer = get_task_tamer()

# Apply custom CSS
apply_custom_css()

# Main app logic
if __name__ == "__main__":
    # Initialize session state for navigation
    if "current_feature" not in st.session_state:
        st.session_state.current_feature = None
    
    # Navigation logic
    if st.session_state.current_feature is None:
        show_home_page(task_tamer)
    elif st.session_state.current_feature == "task_breakdown":
        show_task_page(task_tamer)
    elif st.session_state.current_feature == "summarizer":
        show_summary_page(task_tamer)
    elif st.session_state.current_feature == "quiz":
        show_quiz_page(task_tamer)
    
    # Always show the chat at the bottom
    show_chat_component(task_tamer)