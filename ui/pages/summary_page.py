import streamlit as st
from backend.summarization import summarize_content
from ui.styles import main_header, section_header, warning_box, success_box
import re
from utils.helpers import is_valid_url

def render_summary_page():
    main_header("Content Summarizer")
    
    st.write("Summarize text, web pages, or YouTube videos")
    
    tab1, tab2 = st.tabs(["Text Input", "URL"])
    
    with tab1:
        text_content = st.text_area(
            "Enter the content you want to summarize:", 
            height=200,
            help="Paste the text you want to summarize"
        )
        
        if st.button("Summarize Text"):
            if not text_content:
                warning_box("Please enter some text to summarize")
                return
                
            with st.spinner("Generating summary..."):
                summary = summarize_content(content=text_content)
                
            if summary:
                section_header("Summary")
                st.write(summary)
                
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                warning_box("Could not generate summary. Please try with different content.")
    
    with tab2:
        url = st.text_input(
            "Enter a webpage or YouTube URL:",
            help="Works with most websites and YouTube videos"
        )
        
        if st.button("Summarize URL"):
            if not url:
                warning_box("Please enter a URL")
                return
                
            if not is_valid_url(url):
                warning_box("Please enter a valid URL")
                return
                
            with st.spinner("Fetching content and generating summary..."):
                summary = summarize_content(url=url)
                
            if summary and not summary.startswith("Error"):
                section_header("Summary")
                st.write(summary)
                
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                warning_box(f"Could not generate summary: {summary}")