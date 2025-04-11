import streamlit as st
from ui.pages.home_page import render_home_page
from ui.pages.task_page import render_task_page
from ui.pages.summary_page import render_summary_page
from ui.pages.quiz_page import render_quiz_page
from ui.pages.about_page import render_about_page
from ui.styles import apply_styles

PAGES = {
    "Home": render_home_page,
    "Task Breakdown": render_task_page,
    "Summarization": render_summary_page,
    "Quiz Generator": render_quiz_page,
    "About": render_about_page
}

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
      
        apply_styles()
        
        initialize_session_state()
       
        st.sidebar.title(APP_TITLE)
        selection = st.sidebar.radio("Navigate", list(PAGES.keys()), index=0)
        
        st.info(f"{APP_DESCRIPTION}\n\nMade with ❤️ by {DEVELOPER_NAME}")
        st.markdown("---")
        
        page_function = PAGES.get(selection)
        if page_function:
            page_function()
        else:
            st.error("Page not found. Please select a valid page.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try again or contact support.")

if __name__ == "__main__":
    main()