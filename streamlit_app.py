import streamlit as st
import importlib
from utils.fallback_detector import USING_FALLBACK

# Import UI pages
# Using this approach to handle import errors gracefully
def load_module(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError as e:
        st.error(f"Error loading module {module_name}: {str(e)}")
        return None

home_page = load_module('ui.pages.home_page')
task_page = load_module('ui.pages.task_page')
summary_page = load_module('ui.pages.summary_page')
quiz_page = load_module('ui.pages.quiz_page')
about_page = load_module('ui.pages.about_page')
styles = load_module('ui.styles')

# Configuration for pages
PAGES = {
    "Home": home_page.render_home_page if home_page else None,
    "Task Breakdown": task_page.render_task_page if task_page else None,
    "Summarization": summary_page.render_summary_page if summary_page else None,
    "Quiz Generator": quiz_page.render_quiz_page if quiz_page else None,
    "About": about_page.render_about_page if about_page else None
}

# App metadata
APP_TITLE = "TaskTamer"
APP_DESCRIPTION = (
    "**TaskTamer** helps you manage complex tasks, "
    "summarize content, and test your knowledge."
)
DEVELOPER_NAME = "Alessandra Batalha"

def initialize_session_state():
    """Initialize Streamlit session state if needed."""
    if "initialized" not in st.session_state:
        st.session_state.initialized = True
        st.session_state.task_data = {}
        st.session_state.quiz_history = []
        st.session_state.chat_history = []

def main():
    """Main function to run the Streamlit app."""
    try:
        # Apply custom styles
        if styles:
            styles.apply_styles()
        
        # Initialize session state
        initialize_session_state()
        
        # Display fallback mode if active
        if USING_FALLBACK:
            st.sidebar.warning("⚠️ Running in fallback mode with simplified features. Haystack not available.")
        
        # Sidebar configuration
        st.sidebar.title(APP_TITLE)
        valid_pages = {k: v for k, v in PAGES.items() if v is not None}
        selection = st.sidebar.radio("Navigate", list(valid_pages.keys()), index=0)
        
        # Main content
        st.info(f"{APP_DESCRIPTION}\n\nMade with ❤️ by {DEVELOPER_NAME}")
        st.markdown("---")
        
        # Render selected page
        page_function = valid_pages.get(selection)
        if page_function:
            page_function()
        else:
            st.error("Page not found. Please select a valid page.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try again or contact support.")

if __name__ == "__main__":
    main()