import streamlit as st
import re

def text_input_with_examples(label, examples=None, height=150):
    input_text = st.text_area(label, height=height)
    
    if examples:
        with st.expander("Show examples"):
            for example in examples:
                st.markdown(f"• {example}")
    
    return input_text

def url_input_field(label, help_text=None):
    url = st.text_input(label, help=help_text)
    
    if url and not is_valid_url(url):
        st.warning("Please enter a valid URL")
    
    return url

def is_valid_url(url):
    url_pattern = re.compile(
        r'^(https?:\/\/)?' 
        r'(www\.)?' 
        r'([a-zA-Z0-9-]+\.)+'
        r'[a-zA-Z]{2,}'
        r'(\/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?' 
        r'$'
    )
    return bool(url_pattern.match(url))

def file_upload_area(label, file_types=None):
    if file_types is None:
        file_types = ["txt", "pdf", "docx"]
    
    file_type_str = ", ".join(f".{ft}" for ft in file_types)
    
    uploaded_file = st.file_uploader(label, type=file_types)
    
    if uploaded_file is not None:
        file_details = {
            "filename": uploaded_file.name,
            "filetype": uploaded_file.type,
            "filesize": uploaded_file.size
        }
        st.write(f"File: {file_details['filename']} ({file_details['filesize']} bytes)")
    
    return uploaded_file