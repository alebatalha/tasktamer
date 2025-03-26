"""
Summarizer page UI for TaskTamer.
"""
import streamlit as st
import time
from ..styles import render_header, render_divider, result_container_start, result_container_end
from ..components.inputs import content_input_section

def show_summary_page(task_tamer):
    """
    Display the summarizer interface.
    
    Args:
        task_tamer: TaskTamer instance for backend functionality
    """
    render_header("📝 Summarizer", "Generate concise summaries of your documents")
    
    # Get content from input section
    content = content_input_section(task_tamer)
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Generate Summary", key="summarize"):
            if not content:
                st.error("No content to summarize. Please provide some text, upload a file, or enter a valid URL.")
            else:
                with st.spinner("🧙‍♂️ Conjuring your summary..."):
                    # Add slight delay for visual effect
                    time.sleep(0.5)
                    summary = task_tamer.summarize_text(content)
                
                st.session_state.summary = summary
                st.session_state.original_content = content
    
    with col2:
        if st.button("🏠 Back to Home", key="back_home_summary"):
            st.session_state.current_feature = None
            st.rerun()
    
    # Display results if available
    if "summary" in st.session_state and st.session_state.summary:
        _display_summary(st.session_state.summary, st.session_state.original_content)

def _display_summary(summary, original_content):
    """
    Display the summary and original content.
    
    Args:
        summary: The generated summary
        original_content: The original content that was summarized
    """
    result_container_start()
    st.markdown("### Summary")
    st.write(summary)
    
    # Option to view original
    with st.expander("View Original Content"):
        st.write(original_content)
    
    result_container_end()
    
    # Add options to save
    render_divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Save Summary"):
            st.download_button(
                label="Download",
                data=summary,
                file_name="summary.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("🔄 Start Over", key="reset_summary"):
            if 'summary' in st.session_state:
                del st.session_state.summary
            if 'original_content' in st.session_state:
                del st.session_state.original_content
            st.rerun()