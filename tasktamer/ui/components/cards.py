import streamlit as st

def feature_card(title, description, icon="🔍", on_click=None):
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown(f"<h1 style='text-align: center; font-size: 2.5rem;'>{icon}</h1>", unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
        st.write(description)
    
    if on_click:
        st.button(f"Try {title}", key=f"btn_{title}", on_click=on_click)
    
    st.markdown("---")

def result_card(title, content, allow_download=True, filename="download.txt"):
    st.markdown(f"<h3>{title}</h3>", unsafe_allow_html=True)
    st.write(content)
    
    if allow_download:
        st.download_button(
            label="Download",
            data=content,
            file_name=filename,
            mime="text/plain"
        )