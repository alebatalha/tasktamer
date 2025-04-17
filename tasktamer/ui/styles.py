import streamlit as st

def apply_styles():
    st.markdown("""
    <style>
        .main-header {
            font-size: 2.5rem;
            margin-bottom: 1rem;
        }
        
        .section-header {
            font-size: 1.8rem;
            margin-top: 1.5rem;
            margin-bottom: 1rem;
        }
        
        .info-box {
            background-color: #f0f2f6;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .success-box {
            background-color: #d1e7dd;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .warning-box {
            background-color: #fff3cd;
            border-radius: 0.5rem;
            padding: 1rem;
            margin-bottom: 1rem;
        }
        
        .task-item {
            background-color: #f8f9fa;
            border-left: 4px solid #4b6fff;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 0 0.25rem 0.25rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

def main_header(text):
    st.markdown(f'<h1 class="main-header">{text}</h1>', unsafe_allow_html=True)

def section_header(text):
    st.markdown(f'<h2 class="section-header">{text}</h2>', unsafe_allow_html=True)

def info_box(text):
    st.markdown(f'<div class="info-box">{text}</div>', unsafe_allow_html=True)

def success_box(text):
    st.markdown(f'<div class="success-box">{text}</div>', unsafe_allow_html=True)

def warning_box(text):
    st.markdown(f'<div class="warning-box">{text}</div>', unsafe_allow_html=True)

def task_item(text, idx=None):
    prefix = f"{idx}. " if idx is not None else ""
    st.markdown(f'<div class="task-item">{prefix}{text}</div>', unsafe_allow_html=True)