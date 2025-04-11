import streamlit as st
from ui.styles import main_header, section_header, info_box

def render_about_page():
    main_header("About TaskTamer")
    
    st.write("""
    TaskTamer is a productivity tool designed to help users manage their learning and workflow more effectively. 
    The application combines several powerful features to break down complex tasks, summarize content, and generate 
    quizzes for better knowledge retention.
    """)
    
    section_header("Key Features")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Task Breakdown")
        st.write("Convert complex tasks into manageable, actionable steps")
        
        st.markdown("#### Content Summarization")
        st.write("Extract key insights from text, web pages, and YouTube videos")
    
    with col2:
        st.markdown("#### Quiz Generation")
        st.write("Create interactive quizzes from any content to test your knowledge")
        
        st.markdown("#### AI Assistant")
        st.write("Ask questions about the content and get intelligent responses")
    
    section_header("Technology")
    
    st.write("""
    TaskTamer leverages advanced natural language processing techniques powered by Haystack and state-of-the-art 
    language models. The application uses a modular architecture for flexibility and maintainability, with clean 
    separation between backend logic and frontend presentation.
    """)
    
    st.write("""
    Key technologies used in this project:
    - Streamlit for the user interface
    - Haystack framework for NLP pipelines
    - BeautifulSoup for web scraping
    - FLAN-T5 for language tasks
    """)
    
    section_header("About the Developer")
    
    st.write("""
    TaskTamer was created by **Alessandra Batalha** as part of her final year project at Dublin Business School. 
    The project represents the culmination of her studies in Computer Science, combining practical software 
    engineering skills with artificial intelligence techniques.
    """)
    
    st.write("""
    Alessandra developed TaskTamer with a focus on helping students and professionals manage their learning and 
    work tasks more efficiently. The project demonstrates her skills in full-stack development, natural language 
    processing, and user experience design.
    """)
    
    info_box("""
    <b>Contact:</b><br>
    For more information about this project or to provide feedback, please contact Alessandra Batalha via Dublin Business School.
    """)