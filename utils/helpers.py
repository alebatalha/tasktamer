"""
Helper functions for TaskTamer application.
"""
import os
import tempfile
import streamlit as st
from typing import Dict, Any, List, Optional

def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs("temp", exist_ok=True)

def handle_file_upload(uploaded_file, supported_types: List[str] = None) -> Optional[str]:
    """
    Process an uploaded file and return its content.
    
    Args:
        uploaded_file: The uploaded file from st.file_uploader
        supported_types: List of supported file extensions (without dot)
        
    Returns:
        str: Content of the file or None if processing failed
    """
    if not uploaded_file:
        return None
    
    if supported_types is None:
        supported_types = ["txt", "pdf"]
    
    file_extension = uploaded_file.name.split(".")[-1].lower()
    
    if file_extension not in supported_types:
        st.error(f"Unsupported file type. Please upload one of: {', '.join(supported_types)}")
        return None
    
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=f".{file_extension}") as tmp_file:
            tmp_file.write(uploaded_file.getbuffer())
            file_path = tmp_file.name
        
        # For simple text files, read directly
        if file_extension == "txt":
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            os.unlink(file_path)  # Delete the temp file
            return content
            
        # For PDF files, we would need additional processing
        elif file_extension == "pdf":
            # This would need pdfplumber or PyPDF2 in a real implementation
            st.warning("PDF processing is not fully implemented in this demo.")
            os.unlink(file_path)  # Delete the temp file
            return "PDF content would be extracted here."
    
    except Exception as e:
        st.error(f"Error processing file: {str(e)}")
        return None
    
    finally:
        # Make sure we clean up the temp file if it exists
        if 'file_path' in locals() and os.path.exists(file_path):
            os.unlink(file_path)

def clear_session_state(keys: List[str] = None):
    """
    Clear specific keys from session state.
    
    Args:
        keys: List of keys to clear. If None, no keys are cleared.
    """
    if keys:
        for key in keys:
            if key in st.session_state:
                del st.session_state[key]