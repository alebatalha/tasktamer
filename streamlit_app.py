import streamlit as st
import os
import tempfile
from datetime import datetime
from backend.task_breakdown import break_task
from backend.summarization import summarize_documents
from backend.question_generation import (
    generate_questions_from_text as generate_questions, 
    get_formatted_questions, 
    record_answer, 
    get_quiz_results, 
    get_quiz_download
)
from backend.chat_assistant import ChatAssistant

# Set page configuration
st.set_page_config(
    page_title="TaskTamer",
    page_icon="✅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton button {
        width: 100%;
    }
    .feature-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .chat-container {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .quiz-progress {
        margin-top: 20px;
        margin-bottom: 20px;
    }
    .chat-bubble {
        position: fixed;
        bottom: 20px;
        right: 20px;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background-color: #1976D2;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        cursor: pointer;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        z-index: 9999;
    }
    .team-member-card {
        border: 1px solid #e0e0e0;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .profile-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        background-color: #f0f2f5;
        margin: 0 auto 15px auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
    }
</style>
""", unsafe_allow_html=True)

# Helper function for chat messages
def chat_message(avatar, color, message):
    """Creates a chat-like message container with an avatar"""
    return f"""
    <div style="display: flex; margin-bottom: 10px;">
        <div style="background-color: {color}; color: white; border-radius: 50%; width: 40px; height: 40px; 
                    display: flex; align-items: center; justify-content: center; margin-right: 10px;">
            {avatar}
        </div>
        <div style="background-color: #f0f2f6; padding: 10px; border-radius: 10px; max-width: 80%;">
            {message}
        </div>
    </div>
    """

# Initialize chat assistant
chat_assistant = ChatAssistant()

# Initialize session state variables
if 'quiz_started' not in st.session_state:
    st.session_state.quiz_started = False
if 'current_question' not in st.session_state:
    st.session_state.current_question = 0
if 'quiz_complete' not in st.session_state:
    st.session_state.quiz_complete = False
if 'content' not in st.session_state:
    st.session_state.content = ""
if 'formatted_questions' not in st.session_state:
    st.session_state.formatted_questions = []
if 'page' not in st.session_state:
    st.session_state.page = "Home"
if 'chat_open' not in st.session_state:
    st.session_state.chat_open = False
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 Hi there! I'm Tamy, your TaskTamer assistant. How can I help you today?"},
    ]

def reset_quiz():
    st.session_state.quiz_started = False
    st.session_state.current_question = 0
    st.session_state.quiz_complete = False
    st.session_state.formatted_questions = []

def next_question():
    if st.session_state.current_question < len(st.session_state.formatted_questions) - 1:
        st.session_state.current_question += 1
    else:
        st.session_state.quiz_complete = True

def start_quiz():
    st.session_state.quiz_started = True
    st.session_state.current_question = 0
    st.session_state.quiz_complete = False

def navigate_to(page):
    st.session_state.page = page
    if page != "Quiz":
        reset_quiz()

def toggle_chat():
    st.session_state.chat_open = not st.session_state.chat_open

def add_chat_message(message):
    """Add a user message and generate a response"""
    if message and message.strip():
        # Add user message
        st.session_state.chat_messages.append({"role": "user", "content": message})
        
        # Get response from the chat assistant
        response = chat_assistant.generate_response(message)
        
        # Add assistant response
        st.session_state.chat_messages.append({"role": "assistant", "content": response})
        
        # Log the conversation
        chat_assistant.log_conversation(message, response)

# Function to read text from uploaded file
def read_file_content(uploaded_file):
    if uploaded_file is None:
        return ""
    
    try:
        # For simplicity, we'll just read directly
        content = uploaded_file.getvalue().decode('utf-8', errors='replace')
        return content
    except:
        st.error("Error reading file. Make sure it's a valid text file.")
        return ""

# Chat bubble and window (persistent across all pages)
chat_bubble_html = """
<div id="chat-bubble" style="position: fixed; bottom: 20px; right: 20px; width: 60px; 
     height: 60px; border-radius: 50%; background-color: #1976D2; color: white; 
     display: flex; align-items: center; justify-content: center; font-size: 24px; 
     cursor: pointer; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2); z-index: 999;">
    💬
</div>

<div id="chat-window" style="display: none; position: fixed; bottom: 90px; right: 20px; 
     width: 350px; height: 450px; border-radius: 10px; background-color: white; 
     box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); z-index: 1000; flex-direction: column;">
    <div style="background-color: #1976D2; color: white; padding: 10px 15px; 
         border-top-left-radius: 10px; border-top-right-radius: 10px; 
         font-weight: bold; display: flex; justify-content: space-between; align-items: center;">
        <div>💬 Tamy - TaskTamer Assistant</div>
        <div style="cursor: pointer;" onclick="toggleChatWindow()">✕</div>
    </div>
    <div id="chat-messages" style="flex-grow: 1; padding: 15px; overflow-y: auto; 
         background-color: #f5f5f5; height: 330px;">
"""

# Add all messages to the chat window HTML
for msg in st.session_state.chat_messages:
    if msg["role"] == "user":
        chat_bubble_html += f"""
        <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
            <div style="background-color: #e3f2fd; padding: 8px 12px; border-radius: 18px; max-width: 80%;">
                {msg["content"]}
            </div>
        </div>
        """
    else:
        chat_bubble_html += f"""
        <div style="display: flex; margin-bottom: 10px;">
            <div style="background-color: #1976D2; color: white; border-radius: 50%; 
                 width: 32px; height: 32px; display: flex; align-items: center; 
                 justify-content: center; margin-right: 8px;">
                🤖
            </div>
            <div style="background-color: #eeeeee; padding: 8px 12px; border-radius: 18px; max-width: 80%;">
                {msg["content"]}
            </div>
        </div>
        """

chat_bubble_html += """
    </div>
    <div style="padding: 10px; border-top: 1px solid #e0e0e0; display: flex;">
        <input type="text" id="chat-input" placeholder="Type your message..." 
               style="flex-grow: 1; padding: 8px; border-radius: 20px; border: 1px solid #ddd; margin-right: 8px;">
        <button onclick="sendMessage()" style="background-color: #1976D2; color: white; 
                border: none; border-radius: 20px; padding: 8px 16px;">Send</button>
    </div>
</div>

<script>
function toggleChatWindow() {
    var chatWindow = document.getElementById('chat-window');
    if (chatWindow.style.display === 'none') {
        chatWindow.style.display = 'flex';
    } else {
        chatWindow.style.display = 'none';
    }
}

document.getElementById('chat-bubble').addEventListener('click', function() {
    toggleChatWindow();
});

function sendMessage() {
    var input = document.getElementById('chat-input');
    var message = input.value.trim();
    if (message) {
        // We'll handle the actual sending in Streamlit
        // This just updates the UI temporarily
        var messagesDiv = document.getElementById('chat-messages');
        messagesDiv.innerHTML += `
            <div style="display: flex; justify-content: flex-end; margin-bottom: 10px;">
                <div style="background-color: #e3f2fd; padding: 8px 12px; border-radius: 18px; max-width: 80%;">
                    ${message}
                </div>
            </div>
        `;
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
        input.value = '';
        
        // Submit the form to send the message to Streamlit
        document.getElementById('chat-form').submit();
    }
}

// Scroll to bottom of chat
document.getElementById('chat-messages').scrollTop = document.getElementById('chat-messages').scrollHeight;
</script>
"""

# Inject the chat bubble HTML
st.markdown(chat_bubble_html, unsafe_allow_html=True)

# Create a hidden form to handle chat messages
with st.form(key="chat_form", clear_on_submit=True):
    chat_input = st.text_input("Chat message", key="chat_message_input", label_visibility="collapsed")
    submit_chat = st.form_submit_button("Send", key="chat_submit")
    
    if submit_chat and chat_input:
        add_chat_message(chat_input)
        st.rerun()

# Sidebar navigation
with st.sidebar:
    st.title('✅ TaskTamer')
    
    st.markdown("### Features")
    
    if st.button("🏠 Home", key="nav_home"):
        navigate_to("Home")
        
    if st.button("📝 Breakdown Tasks", key="nav_tasks"):
        navigate_to("Breakdown")
        
    if st.button("📚 Summarize Content", key="nav_summary"):
        navigate_to("Summary")
        
    if st.button("❓ Take a Quiz", key="nav_quiz"):
        navigate_to("Quiz")
        
    if st.button("👥 About Us", key="nav_about"):
        navigate_to("About")
    
    st.markdown("---")
    st.markdown("### Need Help?")
    
    if st.button("💬 Chat with Tamy", key="open_chat"):
        st.session_state.chat_open = True
        st.rerun()
    
    st.markdown("---")
    st.info(
        """
        **TaskTamer** helps you manage complex tasks, 
        summarize content, and test your knowledge.
        
        Made with ❤️ by DBS Students
        """
    )

# Main content area based on navigation
if st.session_state.page == "Home":
    # Home page with nice feature cards
    st.title('Welcome to TaskTamer')
    st.markdown("### Your personal productivity assistant")
    
    st.write("TaskTamer helps you break down complex tasks, summarize documents, and test your knowledge with quizzes.")
    
    # Feature cards in 3 columns
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h1 style='text-align: center; font-size: 40px;'>📝</h1>
            <h3 style='text-align: center;'>Task Breakdown</h3>
            <p>Split complex tasks into manageable steps to stay organized and productive.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Try Task Breakdown", key="home_breakdown"):
            navigate_to("Breakdown")
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h1 style='text-align: center; font-size: 40px;'>📚</h1>
            <h3 style='text-align: center;'>Content Summary</h3>
            <p>Get concise summaries of documents or web content to save time.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Try Content Summary", key="home_summary"):
            navigate_to("Summary")
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h1 style='text-align: center; font-size: 40px;'>❓</h1>
            <h3 style='text-align: center;'>Knowledge Quiz</h3>
            <p>Test your understanding with automatically generated quizzes.</p>
            <br>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Try Knowledge Quiz", key="home_quiz"):
            navigate_to("Quiz")
    
    # Chat assistant introduction on Home page
    st.markdown("""
    <div style="margin-top: 30px; background-color: #e3f2fd; padding: 20px; border-radius: 10px; 
               border-left: 5px solid #1976D2;">
        <div style="display: flex; align-items: center;">
            <div style="background-color: #1976D2; color: white; border-radius: 50%; 
                       width: 60px; height: 60px; display: flex; align-items: center; 
                       justify-content: center; margin-right: 20px; font-size: 30px;">
                🤖
            </div>
            <div>
                <h3 style="margin: 0;">Meet Tamy, Your TaskTamer Assistant!</h3>
                <p style="margin-top: 5px;">I'm here to help you get the most out of TaskTamer. 
                   Ask me anything about breaking down tasks, summarizing content, or creating quizzes!</p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Direct message form on home page
    st.markdown("<h4 style='margin-top: 20px;'>How can I help you today?</h4>", unsafe_allow_html=True)
    
    with st.form(key="home_chat_form", clear_on_submit=True):
        home_message = st.text_input("Ask Tamy a question", placeholder="Example: How do I break down a task?")
        home_submit = st.form_submit_button("Ask Tamy")
        
        if home_submit and home_message:
            add_chat_message(home_message)
            st.rerun()
    
    # Display the latest message exchange on home page
    if len(st.session_state.chat_messages) > 1:
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        
        # Display last user message
        latest_user_idx = next((i for i in range(len(st.session_state.chat_messages)-1, -1, -1) 
                               if st.session_state.chat_messages[i]["role"] == "user"), None)
        
        if latest_user_idx is not None:
            latest_user_msg = st.session_state.chat_messages[latest_user_idx]
            st.markdown(
                chat_message(
                    "👤", 
                    "#666666", 
                    f"<b>You:</b> {latest_user_msg['content']}"
                ), 
                unsafe_allow_html=True
            )
            
            # Display corresponding assistant response if available
            if latest_user_idx + 1 < len(st.session_state.chat_messages):
                latest_assistant_msg = st.session_state.chat_messages[latest_user_idx + 1]
                st.markdown(
                    chat_message(
                        "🤖", 
                        "#1976D2", 
                        f"<b>Tamy:</b> {latest_assistant_msg['content']}"
                    ), 
                    unsafe_allow_html=True
                )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if len(st.session_state.chat_messages) > 3:
            st.markdown("""
            <div style="text-align: center;">
                <a href="#" onclick="document.getElementById('chat-window').style.display='flex';">
                    View full conversation
                </a>
            </div>
            """, unsafe_allow_html=True)
    
    # Testimonial/quote
    st.markdown("---")
    st.markdown("""
    <div style="background-color: #f9f9f9; padding: 20px; border-radius: 10px; text-align: center;">
        <p style="font-style: italic; font-size: 18px;">
        "TaskTamer helped me organize my studies and improved my productivity by 50%!"
        </p>
        <p>— Happy Student</p>
    </div>
    """, unsafe_allow_html=True)

# Breakdown Tasks Page
elif st.session_state.page == "Breakdown":
    st.title('📝 Task Breakdown')
    st.write("Break down complex tasks into manageable steps.")
    
    task = st.text_area("Enter your complex task:", height=100, 
                       placeholder="Example: Write a research paper on renewable energy sources")
    
    if st.button('Break Down Task', key="breakdown_btn"):
        if task:
            with st.spinner('Breaking down your task...'):
                steps = break_task(task)
                
                if steps:
                    st.success("Task successfully broken down into steps!")
                    
                    # Chat-like interface for the steps
                    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                    
                    # First message from TaskTamer
                    st.markdown(
                        chat_message(
                            "✅", 
                            "#2E7D32", 
                            f"I've broken down '<b>{task}</b>' into these steps:"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    # Steps as a separate message
                    steps_html = "<ol>"
                    for step in steps:
                        steps_html += f"<li>{step}</li>"
                    steps_html += "</ol>"
                    
                    st.markdown(
                        chat_message(
                            "📋", 
                            "#1976D2", 
                            steps_html
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    # Final message from TaskTamer
                    st.markdown(
                        chat_message(
                            "💡", 
                            "#2E7D32", 
                            "I recommend tackling one step at a time. Would you like me to help you schedule these tasks?"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Download option
                    steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    
                    st.download_button(
                        label="Download Steps",
                        data=f"TASK: {task}\nBREAKDOWN (Created on {current_date}):\n\n{steps_text}",
                        file_name="task_breakdown.txt",
                        mime="text/plain"
                    )
                else:
                    st.error("No steps could be generated. Please provide a more detailed task description.")
        else:
            st.warning("Please enter a task to break down.")

# Summary Page
elif st.session_state.page == "Summary":
    st.title('📚 Content Summary')
    st.write("Get concise summaries of your documents or text.")
    
    tab1, tab2 = st.tabs(["Text Input", "File Upload"])
    
    with tab1:
        text_content = st.text_area("Enter content to summarize:", height=250, 
                                   placeholder="Paste your text here...")
        if st.button('Summarize Text', key="summarize_text_btn"):
            if text_content:
                with st.spinner('Generating summary...'):
                    st.session_state.content = text_content
                    summary = summarize_documents(text_content)
                    
                    # Chat-like interface for the summary
                    st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                    
                    # Original text as a message (truncated)
                    trunc_content = text_content[:200] + "..." if len(text_content) > 200 else text_content
                    st.markdown(
                        chat_message(
                            "📄", 
                            "#666666", 
                            f"<b>Original Text:</b><br>{trunc_content}"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    # Summary as a message
                    summary_display = summary.split('(Note:')[0] if '(Note:' in summary else summary
                    st.markdown(
                        chat_message(
                            "📚", 
                            "#1976D2", 
                            f"<b>Summary:</b><br>{summary_display}"
                        ), 
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("</div>", unsafe_allow_html=True)
                    
                    # Download option
                    current_date = datetime.now().strftime("%Y-%m-%d")
                    
                    st.download_button(
                        label="Download Summary",
                        data=f"SUMMARY (Created on {current_date}):\n\n{summary}",
                        file_name="content_summary.txt",
                        mime="text/plain"
                    )
            else:
                st.warning("Please enter some text to summarize.")
    
    with tab2:
        uploaded_file = st.file_uploader("Upload a document:", type=['txt'])
        if uploaded_file is not None:
            if st.button('Summarize File', key="summarize_file_btn"):
                with st.spinner('Processing file and generating summary...'):
                    file_content = read_file_content(uploaded_file)
                    st.session_state.content = file_content
                    
                    if file_content:
                        summary = summarize_documents(file_content)
                        
                        # Chat-like interface for the summary
                        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
                        
                        # File information as a message
                        st.markdown(
                            chat_message(
                                "📄", 
                                "#666666", 
                                f"<b>File:</b> {uploaded_file.name}<br><b>Size:</b> {round(len(file_content)/1024, 2)} KB"
                            ), 
                            unsafe_allow_html=True
                        )
                        
                        # Summary as a message
                        summary_display = summary.split('(Note:')[0] if '(Note:' in summary else summary
                        st.markdown(
                            chat_message(
                                "📚", 
                                "#1976D2", 
                                f"<b>Summary:</b><br>{summary_display}"
                            ), 
                            unsafe_allow_html=True
                        )
                        
                        st.markdown("</div>", unsafe_allow_html=True)
                        
                        # Download option
                        current_date = datetime.now().strftime("%Y-%m-%d")
                        
                        st.download_button(
                            label="Download Summary",
                            data=f"SUMMARY OF {uploaded_file.name} (Created on {current_date}):\n\n{summary}",
                            file_name=f"summary_{uploaded_file.name}",
                            mime="text/plain"
                        )
                    else:
                        st.error("Could not read the file content. Please make sure it's a valid text file.")

# Quiz Page
elif st.session_state.page == "Quiz":
    st.title('❓ Knowledge Quiz')
    
    if not st.session_state.quiz_started:
        st.write("Test your understanding with automatically generated questions.")
        
        tab1, tab2 = st.tabs(["Text Input", "File Upload"])