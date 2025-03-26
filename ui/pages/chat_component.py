"""
Chat component UI for TaskTamer.
"""
import streamlit as st
import time
from ..styles import render_divider

def show_chat_component(task_tamer):
    """
    Display the chat assistant interface.
    
    Args:
        task_tamer: TaskTamer instance for chat responses
    """
    render_divider()
    
    # Create expander for chat
    with st.expander("🤖 TaskTamer Assistant - Chat with me for help!", expanded=False):
        st.markdown("""
        <div class="main-header">
            <h3>🤖 TaskTamer Assistant</h3>
            <p>Ask me anything about your tasks or how to use TaskTamer</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Initialize chat history
        if "chat_messages" not in st.session_state:
            st.session_state.chat_messages = [
                {"role": "assistant", "content": "Hi there! I'm your TaskTamer Assistant. How can I help you today?"}
            ]
        
        # Display chat messages from history
        for message in st.session_state.chat_messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # React to user input
        if prompt := st.chat_input("Ask a question about TaskTamer..."):
            # Add user message to chat history
            st.session_state.chat_messages.append({"role": "user", "content": prompt})
            
            # Display user message in chat
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate assistant response
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = task_tamer.get_chat_response(prompt)
                
                # Simulate typing
                response = ""
                for chunk in full_response.split():
                    response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(response + "▌")
                message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.chat_messages.append({"role": "assistant", "content": full_response})