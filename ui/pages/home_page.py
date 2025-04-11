import streamlit as st
from ui.styles import main_header, info_box

def render_home_page():
    main_header("Welcome to TaskTamer")
    
    st.write("TaskTamer is your personal productivity assistant that helps you break down complex tasks, summarize information, and generate quizzes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Task Breakdown")
        st.write("Turn overwhelming tasks into manageable steps")
        if st.button("Try Task Breakdown", key="task_btn"):
            st.session_state["navigation"] = "Task Breakdown"
            st.experimental_rerun()
            
        st.subheader("Summarization")
        st.write("Extract key insights from text, web pages, or YouTube videos")
        if st.button("Try Summarization", key="summary_btn"):
            st.session_state["navigation"] = "Summarization"
            st.experimental_rerun()
            
    with col2:
        st.subheader("Quiz Generator")
        st.write("Create quizzes from your learning materials")
        if st.button("Try Quiz Generator", key="quiz_btn"):
            st.session_state["navigation"] = "Quiz Generator"
            st.experimental_rerun()
    
    info_box("""
    <b>Getting Started:</b>
    <ol>
        <li>Select a feature from the sidebar</li>
        <li>Enter your task or content</li>
        <li>Get instant results!</li>
    </ol>
    """)