"""
Home page UI for TaskTamer application.
"""
import streamlit as st
from ..styles import render_header
from ..components.cards import feature_card

def show_home_page(task_tamer):
    """
    Display the home page with feature cards.
    
    Args:
        task_tamer: TaskTamer instance to check feature availability
    """
    render_header("✨ TaskTamer ✨", "Your magical productivity assistant")
    
    st.markdown("<p>Choose a magical tool to help with your tasks:</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if feature_card("📋", "Task Breaker", "Break complex tasks into manageable steps", "task_breakdown"):
            st.session_state.current_feature = "task_breakdown"
            st.rerun()
    
    with col2:
        if feature_card("📝", "Summarizer", "Generate concise summaries of your documents", "summarizer"):
            st.session_state.current_feature = "summarizer"
            st.rerun()
    
    with col3:
        if feature_card("🧠", "Quiz Master", "Create quizzes to test your knowledge", "quiz"):
            st.session_state.current_feature = "quiz"
            st.rerun()
    
    # Display feature status
    if not task_tamer.is_advanced_available():
        st.warning("⚠️ Running in simplified mode. Some features may have limited functionality.")