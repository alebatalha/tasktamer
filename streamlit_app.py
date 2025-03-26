import streamlit as st
import os
import sys
import time
from pathlib import Path

# Ensure backend directory is in path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

# Import TaskTamer
try:
    from backend import TaskTamer
except ImportError:
    st.error("Could not import TaskTamer. Please check your installation.")
    st.stop()

# Initialize TaskTamer
@st.cache_resource
def get_task_tamer():
    return TaskTamer()

task_tamer = get_task_tamer()

# Set page config
st.set_page_config(
    page_title="TaskTamer",
    page_icon="🧙‍♂️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
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

# App header
def render_header():
    st.markdown("""
    <div class="main-header">
        <h1>✨ TaskTamer ✨</h1>
        <p>Your magical productivity assistant</p>
    </div>
    """, unsafe_allow_html=True)

# Feature card
def feature_card(icon, title, description, key):
    st.markdown(f"""
    <div class="css-card" id="{key}-card">
        <div class="feature-icon">{icon}</div>
        <h3>{title}</h3>
        <p>{description}</p>
    </div>
    """, unsafe_allow_html=True)
    return st.button(f"Use {title}", key=key)

# Main page layout
def main_page():
    render_header()
    
    st.markdown("<p>Choose a magical tool to help with your tasks:</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if feature_card("📋", "Task Breaker", "Break complex tasks into manageable steps", "task_breakdown"):
            st.session_state.current_feature = "task_breakdown"
            st.rerun()
    
    with col2:
        if feature_card("📝", "Summarizer", "Generate concise summaries of your documents", "summarizer"):
            st.session_state.current_feature = "summarizer"
            st.rerun()
    
    with col3:
        if feature_card("🧠", "Quiz Master", "Create quizzes to test your knowledge", "quiz"):
            st.session_state.current_feature = "quiz"
            st.rerun()
    
    # Display feature status
    if not task_tamer.is_advanced_available():
        st.warning("⚠️ Running in simplified mode. Some features may have limited functionality.")

# Task breakdown feature
def task_breakdown_page():
    st.markdown("""
    <div class="main-header">
        <h1>📋 Task Breaker</h1>
        <p>Break complex tasks into manageable steps</p>
    </div>
    """, unsafe_allow_html=True)
    
    task = st.text_area("Enter your complex task:", height=100, 
                         placeholder="Example: Write a research paper on climate change")
    
    col1, col2 = st.columns([1, 3])
    with col1:
        if st.button("Break Down Task", key="break_task"):
            if not task:
                st.error("Please enter a task to break down.")
            else:
                with st.spinner("🧙‍♂️ Breaking down your task..."):
                    # Add slight delay for visual effect
                    time.sleep(0.5)
                    steps = task_tamer.break_task(task)
                
                st.session_state.task_steps = steps
    
    with col2:
        if st.button("🏠 Back to Home", key="back_home_task"):
            st.session_state.current_feature = None
            st.rerun()
    
    # Display results if available
    if "task_steps" in st.session_state and st.session_state.task_steps:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown("### Here's your task breakdown:")
        
        for i, step in enumerate(st.session_state.task_steps, 1):
            step_text = step
            if step.startswith(f"{i}.") or step.startswith(f"{i}:") or step.startswith(f"Step {i}"):
                # If the step already has numbering, don't add another number
                step_text = step
            else:
                step_text = f"{i}. {step}"
                
            col1, col2 = st.columns([0.1, 0.9])
            with col1:
                st.checkbox("", key=f"step_{i}")
            with col2:
                st.markdown(f"**{step_text}**")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add options to save or share
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Save as Text"):
                steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(st.session_state.task_steps)])
                st.download_button(
                    label="Download",
                    data=steps_text,
                    file_name="task_breakdown.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🔄 Start Over"):
                del st.session_state.task_steps
                st.rerun()

# Summarizer feature
def summarizer_page():
    st.markdown("""
    <div class="main-header">
        <h1>📝 Summarizer</h1>
        <p>Generate concise summaries of your documents</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input options
    input_type = st.radio("Choose input type:", ["Text", "Upload File", "Web URL"])
    
    content = ""
    
    if input_type == "Text":
        content = st.text_area("Enter text to summarize:", height=200)
    
    elif input_type == "Upload File":
        uploaded_file = st.file_uploader("Upload a document:", type=['txt', 'pdf'])
        if uploaded_file is not None:
            # Save the file temporarily
            with open("temp_file.txt", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read the file content
            with open("temp_file.txt", "r") as f:
                content = f.read()
            
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    elif input_type == "Web URL":
        url = st.text_input("Enter a webpage URL:")
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if st.button("Fetch Content"):
                with st.spinner("Fetching content..."):
                    content = task_tamer.fetch_webpage_content(url)
                if content == "No readable content found.":
                    st.error("Could not extract readable content from the URL.")
                elif content.startswith("Error"):
                    st.error(content)
                else:
                    st.success("Content fetched successfully!")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Generate Summary", key="summarize"):
            if not content:
                st.error("No content to summarize. Please provide some text, upload a file, or enter a valid URL.")
            else:
                with st.spinner("🧙‍♂️ Conjuring your summary..."):
                    # Add slight delay for visual effect
                    time.sleep(0.5)
                    summary = task_tamer.summarize_text(content)
                
                st.session_state.summary = summary
                st.session_state.original_content = content
    
    with col2:
        if st.button("🏠 Back to Home", key="back_home_summary"):
            st.session_state.current_feature = None
            st.rerun()
    
    # Display results if available
    if "summary" in st.session_state and st.session_state.summary:
        st.markdown("<div class='result-container'>", unsafe_allow_html=True)
        st.markdown("### Summary")
        st.write(st.session_state.summary)
        
        # Option to view original
        with st.expander("View Original Content"):
            st.write(st.session_state.original_content)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Add options to save
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Save Summary"):
                st.download_button(
                    label="Download",
                    data=st.session_state.summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
        
        with col2:
            if st.button("🔄 Start Over", key="reset_summary"):
                if 'summary' in st.session_state:
                    del st.session_state.summary
                if 'original_content' in st.session_state:
                    del st.session_state.original_content
                st.rerun()

# Quiz feature
def quiz_page():
    st.markdown("""
    <div class="main-header">
        <h1>🧠 Quiz Master</h1>
        <p>Create quizzes to test your knowledge</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if we're in quiz taking mode
    if "quiz_questions" in st.session_state and "taking_quiz" in st.session_state and st.session_state.taking_quiz:
        run_quiz()
        return
    
    # Check if we're showing quiz results
    if "quiz_questions" in st.session_state and not st.session_state.get("taking_quiz", False):
        display_quiz_results()
        return
    
    # Input options
    input_type = st.radio("Choose input type:", ["Text", "Upload File", "Web URL"])
    
    content = ""
    
    if input_type == "Text":
        content = st.text_area("Enter text to generate questions from:", height=200)
    
    elif input_type == "Upload File":
        uploaded_file = st.file_uploader("Upload a document:", type=['txt', 'pdf'])
        if uploaded_file is not None:
            # Save the file temporarily
            with open("temp_file.txt", "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Read the file content
            with open("temp_file.txt", "r") as f:
                content = f.read()
            
            st.success(f"File '{uploaded_file.name}' uploaded successfully!")
    
    elif input_type == "Web URL":
        url = st.text_input("Enter a webpage URL:")
        if url:
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            if st.button("Fetch Content"):
                with st.spinner("Fetching content..."):
                    content = task_tamer.fetch_webpage_content(url)
                if content == "No readable content found.":
                    st.error("Could not extract readable content from the URL.")
                elif content.startswith("Error"):
                    st.error(content)
                else:
                    st.success("Content fetched successfully!")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("Generate Quiz", key="generate_quiz"):
            if not content:
                st.error("No content to generate questions from. Please provide some text, upload a file, or enter a valid URL.")
            else:
                with st.spinner("🧙‍♂️ Crafting your quiz..."):
                    # Add slight delay for visual effect
                    time.sleep(0.5)
                    questions = task_tamer.generate_questions(content)
                
                if questions:
                    st.session_state.quiz_questions = questions
                    st.session_state.quiz_score = 0
                    st.session_state.current_question = 0
                    st.session_state.taking_quiz = True
                    st.rerun()
                else:
                    st.error("Could not generate questions from the provided content. Please try different material.")
    
    with col2:
        if st.button("🏠 Back to Home", key="back_home_quiz"):
            st.session_state.current_feature = None
            st.rerun()

def run_quiz():
    questions = st.session_state.quiz_questions
    current = st.session_state.current_question
    
    # Quiz progress
    progress = (current + 1) / len(questions)
    st.progress(progress)
    st.write(f"Question {current + 1} of {len(questions)}")
    
    # Display current question
    q = questions[current]
    st.markdown(f"### {q['question']}")
    
    # Display options
    answer = st.radio("Select your answer:", q['options'], key=f"q_{current}")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Submit Answer"):
            if answer == q['answer']:
                st.success("✅ Correct!")
                if not st.session_state.get(f"answered_{current}", False):
                    st.session_state.quiz_score += 1
                    st.session_state[f"answered_{current}"] = True
            else:
                st.error(f"❌ Incorrect. The correct answer is: {q['answer']}")
                st.session_state[f"answered_{current}"] = True
    
    # Navigation buttons
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
    
    with nav_col1:
        if current > 0:
            if st.button("◀️ Previous"):
                st.session_state.current_question = current - 1
                st.rerun()
    
    with nav_col2:
        if current < len(questions) - 1:
            if st.button("Next ▶️"):
                st.session_state.current_question = current + 1
                st.rerun()
    
    with nav_col3:
        if st.button("End Quiz"):
            st.session_state.taking_quiz = False
            st.rerun()
    
    # Show score at the bottom
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.write(f"Current score: {st.session_state.quiz_score}/{len(questions)}")

def display_quiz_results():
    st.markdown("<div class='result-container'>", unsafe_allow_html=True)
    st.markdown("### Quiz Results")
    
    score = st.session_state.quiz_score
    total = len(st.session_state.quiz_questions)
    percentage = (score / total) * 100
    
    st.markdown(f"<h2 class='success-text'>Your Score: {score}/{total} ({percentage:.1f}%)</h2>", unsafe_allow_html=True)
    
    # Display all questions with correct answers
    st.markdown("### Review Questions")
    
    for i, q in enumerate(st.session_state.quiz_questions):
        with st.expander(f"Question {i+1}: {q['question']}"):
            st.write("**Options:**")
            for option in q['options']:
                if option == q['answer']:
                    st.markdown(f"- ✅ **{option}** (Correct Answer)")
                else:
                    st.write(f"- {option}")
            
            # Show if user got it right
            user_answer = st.session_state.get(f"q_{i}", None)
            if user_answer == q['answer']:
                st.success("You answered this correctly!")
            elif user_answer:
                st.error(f"You selected: {user_answer}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Try New Quiz"):
            for key in ['quiz_questions', 'quiz_score', 'current_question', 'taking_quiz']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
    
    with col2:
        if st.button("🏠 Back to Home", key="quiz_results_home"):
            st.session_state.current_feature = None
            for key in ['quiz_questions', 'quiz_score', 'current_question', 'taking_quiz']:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()
# Chat functionality
def show_chat():
    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    
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
                full_response = generate_assistant_response(prompt)
                
                # Simulate typing
                response = ""
                for chunk in full_response.split():
                    response += chunk + " "
                    time.sleep(0.05)
                    message_placeholder.markdown(response + "▌")
                message_placeholder.markdown(full_response)
            
            # Add assistant response to chat history
            st.session_state.chat_messages.append({"role": "assistant", "content": full_response})

def generate_assistant_response(prompt):
    """Generate assistant responses based on user prompt."""
    # Simple pattern matching for common queries
    prompt_lower = prompt.lower()
    
    # Task breakdown related
    if any(keyword in prompt_lower for keyword in ["break down", "task", "steps", "breakdown"]):
        return "To break down a task, go to the Task Breaker tool from the home page. Enter your complex task, and I'll divide it into manageable steps for you. You can save these steps or mark them as complete as you work through them."
    
    # Summarization related
    elif any(keyword in prompt_lower for keyword in ["summarize", "summary", "shorter", "summarization"]):
        return "The Summarizer tool helps you create concise summaries from text. You can input text directly, upload a document, or enter a web URL. After generating a summary, you can save it for later reference."
    
    # Quiz related
    elif any(keyword in prompt_lower for keyword in ["quiz", "test", "question", "knowledge"]):
        return "The Quiz Master generates multiple-choice questions from your content to test your knowledge. You can input text, upload a document, or use a web URL. After taking the quiz, you'll get a score and can review all questions."
    
    # Help related
    elif any(keyword in prompt_lower for keyword in ["help", "how to", "guide", "tutorial"]):
        return "TaskTamer has three main tools:\n\n1. **Task Breaker**: Breaks complex tasks into steps\n2. **Summarizer**: Creates concise summaries of documents\n3. **Quiz Master**: Generates quizzes to test knowledge\n\nTo use any tool, select it from the home page and follow the instructions. Let me know if you need specific help with any feature!"
    
    # About TaskTamer
    elif any(keyword in prompt_lower for keyword in ["about", "what is", "tasktamer", "purpose"]):
        return "TaskTamer is your magical productivity assistant designed to help you manage complex tasks, understand documents better, and test your knowledge. It combines AI-powered tools with a user-friendly interface to make your learning and productivity journey smoother."
    
    # Fallback response
    else:
        return "I'm here to help you with task breakdown, summarization, and quiz generation in TaskTamer. Could you clarify what you'd like assistance with regarding these features? You can ask about specific tools or how to use them effectively."

# Main app logic
if __name__ == "__main__":
    # Initialize session state for navigation
    if "current_feature" not in st.session_state:
        st.session_state.current_feature = None
    
    # Navigation logic
    if st.session_state.current_feature is None:
        main_page()
    elif st.session_state.current_feature == "task_breakdown":
        task_breakdown_page()
    elif st.session_state.current_feature == "summarizer":
        summarizer_page()
    elif st.session_state.current_feature == "quiz":
        quiz_page()
    
    # Always show the chat at the bottom
    show_chat()