import streamlit as st
from backend.chat_assistant import ask_question
from ui.styles import section_header, warning_box

def render_chat_component():
    section_header("Ask Questions About This Content")
    
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    
    for message in st.session_state.chat_history:
        role = message["role"]
        content = message["content"]
        
        if role == "user":
            st.write(f"You: {content}")
        else:
            st.write(f"TaskTamer: {content}")
    
    question = st.text_input("Ask a question about the content:")
    
    if st.button("Ask"):
        if not question:
            warning_box("Please enter a question")
            return
            
        with st.spinner("Generating answer..."):
            answer = ask_question(question)
            
        st.session_state.chat_history.append({"role": "user", "content": question})
        st.session_state.chat_history.append({"role": "assistant", "content": answer})
        
        st.experimental_rerun()