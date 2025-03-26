"""
Styles module for TaskTamer.
Contains all CSS and styling-related functions.
"""
import streamlit as st

def apply_custom_css():
    """Apply custom CSS to the Streamlit app."""
    st.markdown("""
    <style>
        /* Main container styling */
        .main {
            background-color: #f8f9fa;
        }
        
        /* Header styling */
        h1 {
            color: #4a154b;
            font-weight: 700;
        }
        
        /* Form styling */
        .stTextInput, .stTextArea {
            border-radius: 10px;
        }
        
        /* Button styling */
        .stButton>button {
            background-color: #4a154b;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 1rem;
            font-weight: 600;
            border: none;
        }
        
        .stButton>button:hover {
            background-color: #611f69;
        }
        
        /* Card styling */
        .css-card {
            background-color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        
        /* Success text */
        .success-text {
            color: #28a745;
            font-weight: 600;
        }
        
        /* Main header */
        .main-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Divider */
        .divider {
            margin: 2rem 0;
            border-bottom: 1px solid #ddd;
        }
        
        /* Feature icon */
        .feature-icon {
            font-size: 2rem;
            margin-bottom: 0.5rem;
        }
        
        /* Result container */
        .result-container {
            background-color: #f8f9fa;
            border-radius: 10px;
            padding: 20px;
            margin-top: 20px;
        }
        
        /* Chat styling */
        .stChatFloatingInputContainer {
            border-radius: 20px;
            border: 1px solid #ddd;
        }
        
        .stChatMessage {
            background-color: #f9f9f9;
            border-radius: 15px;
            padding: 10px;
            margin-bottom: 10px;
        }
        
        .stChatMessageContent {
            color: #333;
        }
        
        /* Assistant message */
        .stChatMessage[data-testid="assistant"] {
            background-color: #f0e6f5; /* Light purple for assistant */
        }
        
        /* User message */
        .stChatMessage[data-testid="user"] {
            background-color: #e6f5f0; /* Light green for user */
        }
        
        /* Chat container */
        .chat-container {
            margin-top: 40px;
            padding: 20px;
            border-radius: 15px;
            background-color: white;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }
        
        /* Chat input */
        .stChatInputContainer {
            padding-bottom: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header(title, subtitle=None):
    """
    Render a header with optional subtitle.
    
    Args:
        title: The main title text
        subtitle: Optional subtitle text
    """
    st.markdown(f"""
    <div class="main-header">
        <h1>{title}</h1>
        {f"<p>{subtitle}</p>" if subtitle else ""}
    </div>
    """, unsafe_allow_html=True)

def render_card(icon, title, description, key=None):
    """
    Render a card with icon, title, and description.
    
    Args:
        icon: The icon to display (emoji)
        title: The card title
        description: The card description
        key: Optional unique key for the card
        
    Returns:
        str: HTML for the card
    """
    card_id = key if key else f"card_{title.lower().replace(' ', '_')}"
    return f"""
    <div class="css-card" id="{card_id}">
        <div class="feature-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """

def render_divider():
    """Render a horizontal divider."""
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

def result_container_start():
    """Start a result container section."""
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)

def result_container_end():
    """End a result container section."""
    st.markdown("</div>", unsafe_allow_html=True)