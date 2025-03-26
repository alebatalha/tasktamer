"""
Card UI components for TaskTamer.
"""
import streamlit as st
from ..styles import render_card

def feature_card(icon, title, description, key):
    """
    Create a feature card component with a button.
    
    Args:
        icon: Icon to display (emoji)
        title: Card title
        description: Card description
        key: Unique key for the button
        
    Returns:
        bool: True if the card button was clicked
    """
    st.markdown(render_card(icon, title, description, key), unsafe_allow_html=True)
    return st.button(f"Use {title}", key=key)