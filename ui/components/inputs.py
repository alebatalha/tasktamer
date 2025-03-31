"""
Input UI components for TaskTamer.
"""
import streamlit as st
import time
from urllib.parse import urlparse
from utils.helpers import handle_file_upload

def content_input_section(task_tamer):
    """
    Create a content input section with multiple input options.
    
    Args:
        task_tamer: TaskTamer instance for fetching web content
        
    Returns:
        str: The content from the selected input method
    """
    # Input options
    input_type = st.radio("Choose input type:", ["Text", "Upload File", "Web URL"])
    
    content = ""
    
    if input_type == "Text":
        content = st.text_area("Enter your text:", height=200)
    
    elif input_type == "Upload File":
        uploaded_file = st.file_uploader("Upload a document:", type=['txt', 'pdf'])
        if uploaded_file is not None:
            # Use the helper function to handle file upload
            content = handle_file_upload(uploaded_file)
            if content:
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                # Show a preview
                with st.expander("Preview file content"):
                    st.write(content[:500] + "..." if len(content) > 500 else content)
    
    elif input_type == "Web URL":
        url = st.text_input("Enter a webpage URL:")
        
        if url:
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            # Attempt to fetch content immediately when URL is entered
            try:
                with st.spinner("Fetching content..."):
                    content = task_tamer.fetch_webpage_content(url)
                
                if content == "No readable content found.":
                    st.error("Could not extract readable content from the URL.")
                elif content.startswith("Error"):
                    st.error(content)
                else:
                    st.success(f"Content fetched successfully!")
                    # Show a preview of the content
                    with st.expander("Preview fetched content"):
                        st.write(content[:500] + "..." if len(content) > 500 else content)
            except Exception as e:
                st.error(f"Error processing URL: {str(e)}")
                content = ""  # Reset content if there was an error
    
    # Store the content in session state so it's not lost
    if content:
        st.session_state.current_content = content
    
    # Return content from session state if available and current content is empty
    if not content and "current_content" in st.session_state:
        return st.session_state.current_content
        
    return content