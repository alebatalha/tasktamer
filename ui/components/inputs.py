"""
Input UI components for TaskTamer.
"""
import streamlit as st
import time
import re
from urllib.parse import urlparse

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
            try:
                # Save the file temporarily
                with open("temp_file.txt", "wb") as f:
                    f.write(uploaded_file.getbuffer())
                
                # Read the file content
                with open("temp_file.txt", "r", encoding="utf-8", errors="replace") as f:
                    content = f.read()
                
                st.success(f"File '{uploaded_file.name}' uploaded successfully!")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")
    
    elif input_type == "Web URL":
        url = st.text_input("Enter a webpage URL:")
        
        # URL validation
        if url:
            # Simple URL validation
            url_pattern = re.compile(
                r'^(?:http|https)://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain
                r'localhost|'  # localhost
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
            
            is_valid_url = bool(url_pattern.match(url)) or bool(url_pattern.match(f"https://{url}"))
            
            if not is_valid_url:
                st.warning("Please enter a valid URL (e.g., example.com or https://example.com)")
            
            # Add scheme if missing
            if not url.startswith(('http://', 'https://')):
                processed_url = 'https://' + url
            else:
                processed_url = url
            
            # Display the URL being processed
            st.info(f"URL to process: {processed_url}")
            
            if st.button("Fetch Content"):
                # Check if URL seems valid
                try:
                    result = urlparse(processed_url)
                    if result.netloc and result.scheme:
                        with st.spinner("Fetching content..."):
                            # Visual feedback during fetching
                            progress_bar = st.progress(0)
                            for i in range(100):
                                time.sleep(0.01)
                                progress_bar.progress(i + 1)
                            
                            # Fetch content
                            content = task_tamer.fetch_webpage_content(processed_url)
                            
                        if content == "No readable content found.":
                            st.error("Could not extract readable content from the URL.")
                        elif content.startswith("Error"):
                            st.error(content)
                        else:
                            st.success(f"Content fetched successfully! ({len(content)} characters)")
                            # Show a preview of the content
                            with st.expander("Preview fetched content"):
                                st.write(content[:500] + "..." if len(content) > 500 else content)
                    else:
                        st.error("Invalid URL. Please check the URL and try again.")
                except Exception as e:
                    st.error(f"Error processing URL: {str(e)}")
    
    return content