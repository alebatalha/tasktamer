import streamlit as st
import os
import tempfile
import urllib.parse
from datetime import datetime
from backend.task_breakdown import break_task, suggest_next_action, create_schedule
from backend.summarization import summarize_documents, fetch_webpage_content, is_youtube_url
from backend.question_generation import (
    generate_questions_from_text as generate_questions, 
    get_formatted_questions, 
    record_answer, 
    get_quiz_results, 
    get_quiz_download,
    fetch_webpage_content as quiz_fetch_webpage_content
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
    .chat-message-assistant {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #1976D2;
    }
    .chat-message-user {
        background-color: #e3f2fd;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
        border-left: 4px solid #666666;
        text-align: right;
    }
    .schedule-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 10px;
    }
    .action-tip {
        background-color: #e8f4fd;
        border-left: 4px solid #1976D2;
        padding: 10px 15px;
        margin: 10px 0;
        border-radius: 4px;
    }
    .content-source {
        font-size: 0.9em;
        padding: 5px 10px;
        background-color: #f8f9fa;
        border-radius: 4px;
        margin-bottom: 10px;
        display: inline-block;
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
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = [
        {"role": "assistant", "content": "👋 Hi there! I'm Tamy, your TaskTamer assistant. How can I help you today?"},
    ]
if 'task_steps' not in st.session_state:
    st.session_state.task_steps = []
if 'task_schedule' not in st.session_state:
    st.session_state.task_schedule = []
if 'show_schedule' not in st.session_state:
    st.session_state.show_schedule = False
if 'show_next_actions' not in st.session_state:
    st.session_state.show_next_actions = False
if 'selected_step' not in st.session_state:
    st.session_state.selected_step = None
if 'content_source' not in st.session_state:
    st.session_state.content_source = "Direct Input"

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

# Function to handle URL input
def process_url_input(url):
    """Process a URL input and return the content"""
    if not url:
        return "", "No URL provided"
    
    # Add scheme if missing
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    try:
        # Determine if it's a YouTube URL
        is_youtube = is_youtube_url(url)
        
        with st.spinner("Fetching content from URL..."):
            content = fetch_webpage_content(url)
            
        if is_youtube:
            source_text = "YouTube Video"
        else:
            # Get domain name for regular URLs
            domain = urllib.parse.urlparse(url).netloc
            source_text = f"Web: {domain}"
            
        return content, source_text
    
    except Exception as e:
        st.error(f"Error fetching URL: {str(e)}")
        return "", f"Error: {str(e)}"

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
        st.session_state.page = "Chat"
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
    
    home_message = st.text_input("Ask Tamy a question", placeholder="Example: How do I break down a task?", key="home_chat_input")
    if st.button("Ask Tamy", key="home_chat_btn"):
        if home_message:
            add_chat_message(home_message)
            st.rerun()
    
    # Display the latest message exchange on home page
    if len(st.session_state.chat_messages) > 1:
        st.markdown("<div style='margin-top: 20px;'>", unsafe_allow_html=True)
        
        # Display last user message
        latest_user_idx = next((i for i in range(len(st.session_state.chat_messages)-1, -1, -1) 
                               if st.session_state.chat_messages[i]["role"] == "user"), None)
        
        if latest_user_idx is not None:
            latest_user_msg = st.session_state.chat_messages[latest_user_idx]
            st.markdown(f"""
            <div class="chat-message-user">
                <strong>You:</strong> {latest_user_msg['content']}
            </div>
            """, unsafe_allow_html=True)
            
            # Display corresponding assistant response if available
            if latest_user_idx + 1 < len(st.session_state.chat_messages):
                latest_assistant_msg = st.session_state.chat_messages[latest_user_idx + 1]
                st.markdown(f"""
                <div class="chat-message-assistant">
                    <strong>Tamy:</strong> {latest_assistant_msg['content']}
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if len(st.session_state.chat_messages) > 3:
            if st.button("View full conversation", key="view_full_chat"):
                st.session_state.page = "Chat"
                st.rerun()
    
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

# Chat Page
elif st.session_state.page == "Chat":
    st.title('💬 Chat with Tamy')
    st.write("Ask me anything about TaskTamer's features and how to use them effectively.")
    
    # Display chat history
    for msg in st.session_state.chat_messages:
        if msg["role"] == "user":
            st.markdown(f"""
            <div class="chat-message-user">
                <strong>You:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="chat-message-assistant">
                <strong>Tamy:</strong> {msg['content']}
            </div>
            """, unsafe_allow_html=True)
    
    # Chat input
    chat_message = st.text_input("Type your message...", key="chat_message_input")
    col1, col2 = st.columns([4, 1])
    with col2:
        if st.button("Send", key="send_chat_message"):
            if chat_message:
                add_chat_message(chat_message)
                st.rerun()

# Breakdown Tasks Page
elif st.session_state.page == "Breakdown":
    st.title('📝 Task Breakdown')
    st.write("Break down complex tasks into manageable steps.")
    
    # Only show input if we don't have steps yet or if reset
    if not st.session_state.task_steps or st.session_state.show_schedule or st.session_state.show_next_actions:
        task = st.text_area("Enter your complex task:", height=100, 
                           placeholder="Example: Write a research paper on renewable energy sources")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            if st.button('Break Down Task', key="breakdown_btn"):
                if task:
                    with st.spinner('Breaking down your task...'):
                        steps = break_task(task)
                        
                        if steps:
                            st.session_state.task_steps = steps
                            st.session_state.original_task = task
                            st.session_state.show_schedule = False
                            st.session_state.show_next_actions = False
                            st.session_state.selected_step = None
                            # Also generate a schedule
                            st.session_state.task_schedule = create_schedule(steps)
                            st.rerun()
                        else:
                            st.error("No steps could be generated. Please provide a more detailed task description.")
                else:
                    st.warning("Please enter a task to break down.")
    
    # Display task steps if available
    if st.session_state.task_steps and not st.session_state.show_schedule and not st.session_state.show_next_actions:
        st.success("Task successfully broken down into steps!")
        
        # Chat-like interface for the steps
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        
        # First message from TaskTamer
        st.markdown(
            chat_message(
                "✅", 
                "#2E7D32", 
                f"I've broken down '<b>{st.session_state.original_task}</b>' into these steps:"
            ), 
            unsafe_allow_html=True
        )
        
        # Steps as a separate message
        steps_html = "<ol>"
        for step in st.session_state.task_steps:
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
                "I recommend tackling one step at a time. Would you like me to help you schedule these tasks or suggest specific actions?"
            ), 
            unsafe_allow_html=True
        )
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Action buttons for next steps
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📅 Create Schedule", key="create_schedule"):
                st.session_state.show_schedule = True
                st.rerun()
        
        with col2:
            if st.button("🔍 Get Next Actions", key="next_actions"):
                st.session_state.show_next_actions = True
                st.rerun()
                
        with col3:
            # Download option
            steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(st.session_state.task_steps)])
            current_date = datetime.now().strftime("%Y-%m-%d")
            
            st.download_button(
                label="📥 Download Steps",
                data=f"TASK: {st.session_state.original_task}\nBREAKDOWN (Created on {current_date}):\n\n{steps_text}",
                file_name="task_breakdown.txt",
                mime="text/plain"
            )
    
    # Show schedule if requested
    elif st.session_state.show_schedule and st.session_state.task_schedule:
        st.subheader("📅 Suggested Schedule")
        st.markdown("Here's a suggested schedule to help you complete your task efficiently:")
        
        for i, item in enumerate(st.session_state.task_schedule):
            st.markdown(f"""
            <div class="schedule-card">
                <strong>Step {i+1}:</strong> {item['step']}<br>
                <strong>Date:</strong> {item['date']}<br>
                <strong>Time:</strong> {item['time_slot']}<br>
                <strong>Estimated Duration:</strong> {item['estimate']}
            </div>
            """, unsafe_allow_html=True)
        
        # Download schedule
        schedule_text = "TASK SCHEDULE\n\n"
        schedule_text += f"Task: {st.session_state.original_task}\n"
        schedule_text += f"Created on: {datetime.now().strftime('%Y-%m-%d')}\n\n"
        
        for i, item in enumerate(st.session_state.task_schedule):
            schedule_text += f"Step {i+1}: {item['step']}\n"
            schedule_text += f"Date: {item['date']}\n"
            schedule_text += f"Time: {item['time_slot']}\n"
            schedule_text += f"Est. Duration: {item['estimate']}\n\n"
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.download_button(
                label="📥 Download Schedule",
                data=schedule_text,
                file_name="task_schedule.txt",
                mime="text/plain"
            )
            
        with col2:
            if st.button("← Back to Steps", key="back_to_steps_schedule"):
                st.session_state.show_schedule = False
                st.rerun()
    
    # Show next actions if requested
    elif st.session_state.show_next_actions and st.session_state.task_steps:
        st.subheader("🔍 Next Actions for Each Step")
        st.markdown("Select a step to get specific suggestions for what to do next:")
        
        # Step selector
        selected_step_idx = st.selectbox(
            "Choose a step:",
            range(len(st.session_state.task_steps)),
            format_func=lambda x: f"Step {x+1}: {st.session_state.task_steps[x][:50]}..."
        )
        
        if selected_step_idx is not None:
            selected_step = st.session_state.task_steps[selected_step_idx]
            
            # Get next action for the selected step
            next_action = suggest_next_action(selected_step)
            
            st.markdown(f"""
            <div class="schedule-card">
                <strong>Step {selected_step_idx+1}:</strong> {selected_step}
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="action-tip">
                <strong>💡 Suggested Action:</strong><br>
                {next_action}
            </div>
            """, unsafe_allow_html=True)
            
            # Additional action input
            st.markdown("### Add Your Own Action")
            custom_action = st.text_area("What specific action will you take for this step?", 
                                         placeholder="Example: I'll spend 30 minutes researching this topic tonight.")
            
            if st.button("Save Action", key="save_action"):
                if custom_action:
                    if 'step_actions' not in st.session_state:
                        st.session_state.step_actions = {}
                    
                    st.session_state.step_actions[selected_step_idx] = custom_action
                    st.success(f"Action saved for Step {selected_step_idx+1}!")
            
            # Show all saved actions
            if 'step_actions' in st.session_state and st.session_state.step_actions:
                st.markdown("### Your Saved Actions")
                
                for step_idx, action in st.session_state.step_actions.items():
                    if step_idx < len(st.session_state.task_steps):
                        st.markdown(f"""
                        <div style="padding: 10px; border-left: 3px solid #28a745; margin-bottom: 10px;">
                            <strong>Step {step_idx+1}:</strong> {st.session_state.task_steps[step_idx][:50]}...<br>
                            <strong>Your Action:</strong> {action}
                        </div>
                        """, unsafe_allow_html=True)
        
        # Back button
        if st.button("← Back to Steps", key="back_to_steps_actions"):
            st.session_state.show_next_actions = False
            st.rerun()
    
    # Reset button - always show at bottom
    st.markdown("---")
    if st.button("🔄 Start Over with New Task", key="reset_task"):
        st.session_state.task_steps = []
        st.session_state.task_schedule = []
        st.session_state.show_schedule = False
        st.session_state.show_next_actions = False
        st.session_state.selected_step = None
        if 'step_actions' in st.session_state:
            del st.session_state.step_actions
        st.rerun()

# Summary Page
elif st.session_state.page == "Summary":
    st.title('📚 Content Summary')
    st.write("Get concise summaries of your documents or text.")
    
    # Source selection
    source_type = st.radio("Choose source type:", ["Text Input", "File Upload", "Web URL", "YouTube Video"])
    
    # Collect content based on source type
    content = ""
    source_text = "Direct Input"
    
    if source_type == "Text Input":
        text_content = st.text_area("Enter content to summarize:", height=250, 
                                   placeholder="Paste your text here...")
        content = text_content
        
    elif source_type == "File Upload":
        uploaded_file = st.file_uploader("Upload a document:", type=['txt'])
        if uploaded_file is not None:
            file_content = read_file_content(uploaded_file)
            content = file_content
            source_text = f"File: {uploaded_file.name}"
    
    elif source_type == "Web URL" or source_type == "YouTube Video":
        url = st.text_input("Enter URL:", 
                            placeholder="Example: https://example.com or https://www.youtube.com/watch?v=...")
        if url:
            content, source_text = process_url_input(url)
    
    # Generate summary button
    if st.button('Generate Summary', key="summarize_btn"):
        if content:
            with st.spinner('Generating summary...'):
                st.session_state.content = content
                st.session_state.content_source = source_text
                summary = summarize_documents(content)
                
                if summary:
                    st.session_state.summary = summary
                    st.rerun()
                else:
                    st.error("Could not generate a summary. The content may be too short or not suitable for summarization.")
        else:
            st.warning("Please provide some content to summarize.")
    
    # Display summary if available
    if 'summary' in st.session_state and st.session_state.summary:
        st.success("Summary generated successfully!")
        
        # Source indicator
        st.markdown(f"<span class='content-source'>{st.session_state.content_source}</span>", unsafe_allow_html=True)
        
        # Chat-like interface for the summary
        st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
        
        # Original text as a message (truncated)
        original_content = st.session_state.content
        trunc_content = original_content[:200] + "..." if len(original_content) > 200 else original_content
        st.markdown(
            chat_message(
                "📄", 
                "#666666", 
                f"<b>Original Content:</b><br>{trunc_content}"
            ), 
            unsafe_allow_html=True
        )
        
        # Summary as a message
        summary = st.session_state.summary
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
            data=f"SUMMARY (Created on {current_date})\n\nSource: {st.session_state.content_source}\n\n{summary}",
            file_name="content_summary.txt",
            mime="text/plain"
        )
        
        # Reset button
        if st.button("Generate New Summary", key="reset_summary"):
            if 'summary' in st.session_state:
                del st.session_state.summary
                del st.session_state.content
                del st.session_state.content_source
            st.rerun()

# Quiz Page (continued)
elif st.session_state.page == "Quiz":
    st.title('❓ Knowledge Quiz')
    
    if not st.session_state.quiz_started:
        st.write("Test your understanding with automatically generated questions.")
        
        # Source selection
        source_type = st.radio("Choose source type:", ["Text Input", "File Upload", "Web URL", "YouTube Video"])
        
        # Collect content based on source type
        content = ""
        source_text = "Direct Input"
        
        if source_type == "Text Input":
            text_content = st.text_area("Enter content to create a quiz from:", height=250, 
                                       placeholder="Paste your text here...")
            content = text_content
            
        elif source_type == "File Upload":
            uploaded_file = st.file_uploader("Upload a document:", type=['txt'])
            if uploaded_file is not None:
                file_content = read_file_content(uploaded_file)
                content = file_content
                source_text = f"File: {uploaded_file.name}"
        
        elif source_type == "Web URL" or source_type == "YouTube Video":
            url = st.text_input("Enter URL:", 
                                placeholder="Example: https://example.com or https://www.youtube.com/watch?v=...")
            if url:
                content, source_text = process_url_input(url)
        
        # Number of questions slider
        num_questions = st.slider("Number of questions:", min_value=1, max_value=10, value=5)
        
        # Generate quiz button
        if st.button('Generate Quiz', key="generate_quiz_btn"):
            if content:
                with st.spinner('Creating quiz questions...'):
                    st.session_state.content = content
                    st.session_state.content_source = source_text
                    questions = generate_questions(content, num_questions)
                    
                    if questions:
                        st.session_state.formatted_questions = get_formatted_questions()
                        start_quiz()
                        st.rerun()
                    else:
                        st.error("Failed to generate questions. The content may be too short or not suitable for quiz generation.")
            else:
                st.warning("Please provide some content to create a quiz from.")
    
    # Display quiz if started
    elif st.session_state.quiz_started and not st.session_state.quiz_complete:
        questions = st.session_state.formatted_questions
        
        if questions and st.session_state.current_question < len(questions):
            current_q = questions[st.session_state.current_question]
            
            # Source indicator
            st.markdown(f"<span class='content-source'>Quiz source: {st.session_state.content_source}</span>", unsafe_allow_html=True)
            
            # Progress indicator
            st.markdown("<div class='quiz-progress'>", unsafe_allow_html=True)
            st.progress((st.session_state.current_question) / len(questions))
            st.write(f"Question {st.session_state.current_question + 1} of {len(questions)}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Display question in a card-like container
            st.markdown(f"""
            <div style="background-color: #f0f8ff; padding: 20px; border-radius: 10px; margin-bottom: 20px;">
                <h3>❓ {current_q['question']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            # Create radio buttons for options
            answer = st.radio(
                "Select your answer:",
                current_q['options'],
                key=f"q_{st.session_state.current_question}"
            )
            
            # Submit button
            col1, col2, col3 = st.columns([1, 1, 1])
            with col2:
                if st.button('Submit Answer', key="submit_answer"):
                    # Record the answer
                    record_answer(current_q['question_idx'], answer)
                    next_question()
                    st.rerun()
    
    # Show results when quiz is complete
    if st.session_state.quiz_complete:
        results = get_quiz_results()
        
        # Display score with appropriate emoji based on percentage
        score_emoji = "🎉" if results['percentage'] >= 80 else "👍" if results['percentage'] >= 60 else "🤔"
        st.markdown(f"""
        <div style="background-color: #e8f5e9; padding: 20px; border-radius: 10px; text-align: center; margin-bottom: 20px;">
            <h2>{score_emoji} Quiz Complete!</h2>
            <h3>Your score: {results['score']}/{results['total']} ({results['percentage']:.1f}%)</h3>
            <p>{results['feedback']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display all questions with correct/incorrect answers
        st.subheader("📋 Review Questions")
        
        for i, q in enumerate(st.session_state.formatted_questions):
            with st.expander(f"Question {i+1}: {q['question']}"):
                st.write("Options:")
                for opt in q['options']:
                    if opt == q['correct_answer']:
                        st.markdown(f"- **{opt}** ✓")
                    else:
                        st.write(f"- {opt}")
                
                st.write(f"**Correct answer:** {q['correct_answer']}")
        
        # Download options
        st.subheader("💾 Download Quiz")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = get_quiz_download(format='csv')
            st.download_button(
                label="Download as CSV",
                data=csv_data,
                file_name="task_tamer_quiz.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = get_quiz_download(format='json')
            st.download_button(
                label="Download as JSON",
                data=json_data,
                file_name="task_tamer_quiz.json",
                mime="application/json"
            )
        
        with col3:
            text_data = get_quiz_download(format='text')
            st.download_button(
                label="Download as Text",
                data=text_data,
                file_name="task_tamer_quiz.txt",
                mime="text/plain"
            )
        
        # Option to restart
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Start New Quiz", key="new_quiz"):
            reset_quiz()
            st.rerun()

# About Us Page
elif st.session_state.page == "About":
    st.title('👥 About Us')
    st.write("Meet the team behind TaskTamer and learn about our mission.")
    
    st.markdown("""
    <div style="background-color: #f5f5f5; padding: 25px; border-radius: 10px; margin-bottom: 30px;">
        <h3>Our Mission</h3>
        <p>TaskTamer was created to help students and professionals manage their workload more effectively. 
           We believe that by breaking down complex tasks, summarizing important information, and 
           reinforcing knowledge through quizzes, anyone can boost their productivity and learning.</p>
        
        <h3>Our Story</h3>
        <p>TaskTamer began as a final year project at Dublin Business School. Our goal was to create a tool that 
           simplifies complex tasks and makes learning more efficient. After researching productivity challenges faced by students,
           we developed TaskTamer to address these needs in a user-friendly way.</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Meet the Developer
    st.subheader("Meet the Developer")
    
    st.markdown("""
    <div class="team-member-card">
        <div class="profile-circle">👩‍💻</div>
        <h3>Alessandra Batalha</h3>
        <p>Lead Developer</p>
        <p><em>"I'm passionate about creating tools that help people learn and work more efficiently."</em></p>
        <div style="margin-top: 15px;">
            <p>As the lead developer of TaskTamer, Alessandra combined her interest in productivity systems 
            with her technical skills to create this application. With a background in computer science and 
            experience in educational technology, she designed TaskTamer to address common challenges faced 
            by students and professionals.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Features and Technologies section
    st.subheader("Features and Technologies")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
            <h4>Key Features</h4>
            <ul>
                <li>Task breakdown with actionable steps</li>
                <li>Document and web content summarization</li>
                <li>YouTube video transcript processing</li>
                <li>Knowledge quiz generation</li>
                <li>Chat assistant for guidance</li>
                <li>Scheduling and action planning</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background-color: #f8f9fa; padding: 15px; border-radius: 8px;">
            <h4>Technologies Used</h4>
            <ul>
                <li>Python</li>
                <li>Streamlit</li>
                <li>Natural Language Processing</li>
                <li>Web Scraping</li>
                <li>Text Analysis</li>
                <li>AI Assistants</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Future plans section
    st.markdown("""
    <div style="margin-top: 30px; padding: 20px; border-radius: 10px; background-color: #e8f4fd; border-left: 4px solid #1976D2;">
        <h3>Future Plans</h3>
        <p>We're constantly working to improve TaskTamer. Some features we're planning to add include:</p>
        <ul>
            <li>Enhanced AI-powered task breakdown</li>
            <li>More sophisticated summarization algorithms</li>
            <li>Integration with calendar apps for scheduling</li>
            <li>Collaborative features for team projects</li>
            <li>Mobile application for on-the-go productivity</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Contact information
    st.markdown("""
    <div style="text-align: center; margin-top: 30px;">
        <h3>Get in Touch</h3>
        <p>We'd love to hear your feedback and suggestions!</p>
        <p>Email: alessandra.batalha@example.com</p>
        <p>GitHub: github.com/alessandrabatalha/tasktamer</p>
    </div>
    """, unsafe_allow_html=True)