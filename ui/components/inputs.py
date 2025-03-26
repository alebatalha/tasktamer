"""
Input UI components for TaskTamer.
"""
import streamlit as st
import time

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
            # Save the file temporarily
            with open("temp_file.txt", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read the file content
            with open("temp_file.txt", "r") as f:
                content = f.read()
            
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    elif input_type == "Web URL":
        url = st.text_input("Enter a webpage URL:")
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if st.button("Fetch Content"):
                with st.spinner("Fetching content..."):
                    content = task_tamer.fetch_webpage_content(url)
                if content == "No readable content found.":
                    st.error("Could not extract readable content from the URL.")
                elif content.startswith("Error"):
                    st.error(content)
                else:
                    st.success("Content fetched successfully!")
    
    return content