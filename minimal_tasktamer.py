import streamlit as st
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import json

# App metadata
APP_TITLE = "TaskTamer"
APP_DESCRIPTION = (
    "**TaskTamer** helps you manage complex tasks, "
    "summarize content, and test your knowledge."
)
DEVELOPER_NAME = "Alessandra Batalha"

# Apply custom styles
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
        
        .task-item {
            background-color: #f8f9fa;
            border-left: 4px solid #4b6fff;
            padding: 0.75rem;
            margin-bottom: 0.5rem;
            border-radius: 0 0.25rem 0.25rem 0;
        }
    </style>
    """, unsafe_allow_html=True)

# Helper functions
def fetch_webpage_content(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        for tag in soup(['script', 'style', 'header', 'footer', 'nav']):
            tag.decompose()
            
        paragraphs = soup.find_all("p")
        text = "\n".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
        
        if not text:
            main_content = soup.find('main') or soup.find('article') or soup.find('body')
            if main_content:
                text = main_content.get_text(separator="\n", strip=True)
            
        return text if text else "No readable content found."
    except Exception as e:
        return f"Error fetching webpage: {str(e)}"

def is_valid_url(url):
    url_pattern = re.compile(
        r'^(https?:\/\/)?' 
        r'(www\.)?' 
        r'([a-zA-Z0-9-]+\.)+'
        r'[a-zA-Z]{2,}'
        r'(\/[a-zA-Z0-9-._~:/?#[\]@!$&\'()*+,;=]*)?' 
        r'$'
    )
    return bool(url_pattern.match(url))

# Simple task breakdown (without using LLM)
def simple_break_task(task):
    # Simple rule-based task breakdown
    steps = []
    
    if "research" in task.lower():
        steps.append("Define your research topic and goals")
        steps.append("Gather relevant sources and materials")
        steps.append("Take notes from your sources")
        steps.append("Organize your information")
        steps.append("Create an outline")
        steps.append("Write a first draft")
        steps.append("Revise and edit your work")
    elif "presentation" in task.lower():
        steps.append("Define your presentation topic and audience")
        steps.append("Research key information")
        steps.append("Create an outline")
        steps.append("Design slides or visual aids")
        steps.append("Practice your delivery")
        steps.append("Get feedback and revise")
        steps.append("Finalize your presentation")
    elif "project" in task.lower():
        steps.append("Define project scope and objectives")
        steps.append("Create a timeline with milestones")
        steps.append("Identify required resources")
        steps.append("Assign responsibilities")
        steps.append("Track progress and adjust as needed")
        steps.append("Review and quality check")
        steps.append("Finalize and deliver")
    else:
        # Generic task breakdown
        steps.append("Define your goal and desired outcome")
        steps.append("Break down the main components")
        steps.append("Create a timeline")
        steps.append("Gather necessary resources")
        steps.append("Work through each component")
        steps.append("Review progress regularly")
        steps.append("Complete final review")
    
    return steps

# Simple summarizer (rule-based, not using LLM)
def simple_summarize(text):
    if not text:
        return "No text provided to summarize."
    
    # Extract sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Simple heuristic: take first sentence, middle sentence, and last sentence
    if len(sentences) <= 3:
        return text
    
    summary = [
        sentences[0],
        sentences[len(sentences) // 2],
        sentences[-1]
    ]
    
    return " ".join(summary)

# Simple quiz generator (rule-based)
def simple_generate_quiz(text, num_questions=3):
    if not text:
        return []
    
    # Split into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    
    # Take a few sentences to create questions from
    selected_sentences = []
    step = max(1, len(sentences) // (num_questions + 1))
    
    for i in range(0, min(len(sentences), num_questions * step), step):
        if i < len(sentences):
            selected_sentences.append(sentences[i])
    
    # Create simple quiz questions
    quiz = []
    
    for i, sentence in enumerate(selected_sentences[:num_questions]):
        # Create a simple fill-in-the-blank question
        words = sentence.split()
        if len(words) < 4:
            continue
            
        # Pick a word to remove (not first or last word)
        word_index = len(words) // 2
        correct_word = words[word_index]
        
        # Create incorrect options
        incorrect_options = ["option A", "option B", "option C"]
        
        question = " ".join(words[:word_index] + ["_____"] + words[word_index+1:])
        
        quiz.append({
            "question": f"Fill in the blank: {question}",
            "options": [correct_word] + incorrect_options,
            "answer": correct_word
        })
    
    return quiz

# Page renderers
def render_home_page():
    st.markdown('<h1 class="main-header">Welcome to TaskTamer</h1>', unsafe_allow_html=True)
    
    st.write("TaskTamer is your personal productivity assistant that helps you break down complex tasks, summarize information, and generate quizzes.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Task Breakdown")
        st.write("Turn overwhelming tasks into manageable steps")
            
        st.subheader("Summarization")
        st.write("Extract key insights from text and web pages")
    
    with col2:
        st.subheader("Quiz Generator")
        st.write("Create quizzes from your learning materials")
    
    st.markdown(
        '<div class="info-box">'
        '<b>Getting Started:</b>'
        '<ol>'
        '<li>Select a feature from the sidebar</li>'
        '<li>Enter your task or content</li>'
        '<li>Get instant results!</li>'
        '</ol>'
        '</div>', 
        unsafe_allow_html=True
    )

def render_task_page():
    st.markdown('<h1 class="main-header">Task Breakdown</h1>', unsafe_allow_html=True)
    
    with st.form(key="task_form"):
        task_description = st.text_area(
            "Enter a complex task you want to break down:", 
            height=150,
            help="Describe your task in detail for better results"
        )
        
        examples = st.expander("Show examples")
        with examples:
            st.write("• Write a research paper on AI ethics")
            st.write("• Create a personal budget plan for the next year")
            st.write("• Organize a virtual conference for 100+ attendees")
        
        submit_button = st.form_submit_button("Break Down Task")
    
    if submit_button:
        if not task_description:
            st.warning("Please enter a task description")
            return
            
        with st.spinner("Breaking down your task..."):
            steps = simple_break_task(task_description)
            
        if steps:
            st.markdown('<h2 class="section-header">Here\'s your task breakdown:</h2>', unsafe_allow_html=True)
            
            for i, step in enumerate(steps, 1):
                st.markdown(
                    f'<div class="task-item">{i}. {step}</div>', 
                    unsafe_allow_html=True
                )
                
            st.download_button(
                label="Download Task Breakdown",
                data="\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)]),
                file_name="task_breakdown.txt",
                mime="text/plain"
            )
        else:
            st.warning("Could not generate steps. Please try rewording your task.")

def render_summary_page():
    st.markdown('<h1 class="main-header">Content Summarizer</h1>', unsafe_allow_html=True)
    
    st.write("Summarize text or web pages")
    
    tab1, tab2 = st.tabs(["Text Input", "URL"])
    
    with tab1:
        text_content = st.text_area(
            "Enter the content you want to summarize:", 
            height=200,
            help="Paste the text you want to summarize"
        )
        
        if st.button("Summarize Text"):
            if not text_content:
                st.warning("Please enter some text to summarize")
                return
                
            with st.spinner("Generating summary..."):
                summary = simple_summarize(text_content)
                
            if summary:
                st.markdown('<h2 class="section-header">Summary</h2>', unsafe_allow_html=True)
                st.write(summary)
                
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.warning("Could not generate summary. Please try with different content.")
    
    with tab2:
        url = st.text_input(
            "Enter a webpage URL:",
            help="Works with most websites"
        )
        
        if st.button("Summarize URL"):
            if not url:
                st.warning("Please enter a URL")
                return
                
            if not is_valid_url(url):
                st.warning("Please enter a valid URL")
                return
                
            with st.spinner("Fetching content and generating summary..."):
                content = fetch_webpage_content(url)
                summary = simple_summarize(content)
                
            if summary and not summary.startswith("Error"):
                st.markdown('<h2 class="section-header">Summary</h2>', unsafe_allow_html=True)
                st.write(summary)
                
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )
            else:
                st.warning(f"Could not generate summary: {summary}")

def render_quiz_page():
    st.markdown('<h1 class="main-header">Quiz Generator</h1>', unsafe_allow_html=True)
    
    st.write("Create quizzes from text or web pages")
    
    tab1, tab2 = st.tabs(["Text Input", "URL"])
    
    with tab1:
        text_content = st.text_area(
            "Enter the content you want to create a quiz from:", 
            height=200,
            help="Paste the text you want to create a quiz from"
        )
        
        num_questions = st.slider("Number of questions", 1, 5, 3)
        
        if st.button("Generate Quiz", key="text_quiz_btn"):
            if not text_content:
                st.warning("Please enter some text to generate a quiz from")
                return
                
            with st.spinner("Generating quiz..."):
                quiz = simple_generate_quiz(text_content, num_questions=num_questions)
                
            display_quiz(quiz)
    
    with tab2:
        url = st.text_input(
            "Enter a webpage URL:",
            help="Works with most websites"
        )
        
        num_questions = st.slider("Number of questions", 1, 5, 3, key="url_num_q")
        
        if st.button("Generate Quiz", key="url_quiz_btn"):
            if not url:
                st.warning("Please enter a URL")
                return
                
            if not is_valid_url(url):
                st.warning("Please enter a valid URL")
                return
                
            with st.spinner("Fetching content and generating quiz..."):
                content = fetch_webpage_content(url)
                quiz = simple_generate_quiz(content, num_questions=num_questions)
                
            display_quiz(quiz)

def display_quiz(quiz_data):
    if not quiz_data:
        st.warning("Could not generate quiz. Please try with different content.")
        return
        
    st.markdown('<h2 class="section-header">Your Quiz</h2>', unsafe_allow_html=True)
    
    if "quiz_answers" not in st.session_state:
        st.session_state.quiz_answers = {}
        st.session_state.quiz_submitted = False
        st.session_state.quiz_score = 0
    
    for i, question in enumerate(quiz_data):
        st.subheader(f"Question {i+1}")
        st.write(question.get("question", ""))
        
        options = question.get("options", [])
        if options:
            answer_key = f"q_{i}"
            st.session_state.quiz_answers[answer_key] = question.get("answer", "")
            
            st.radio(
                "Select your answer:",
                options,
                key=f"quiz_{i}"
            )
    
    if st.button("Submit Quiz"):
        st.session_state.quiz_submitted = True
        st.session_state.quiz_score = 0
        
        for i in range(len(quiz_data)):
            answer_key = f"q_{i}"
            selected = st.session_state[f"quiz_{i}"]
            
            if selected == st.session_state.quiz_answers[answer_key]:
                st.session_state.quiz_score += 1
        
        score_percentage = (st.session_state.quiz_score / len(quiz_data)) * 100
        st.success(f"Your score: {st.session_state.quiz_score}/{len(quiz_data)} ({score_percentage:.1f}%)")
        
        for i in range(len(quiz_data)):
            answer_key = f"q_{i}"
            selected = st.session_state[f"quiz_{i}"]
            correct = st.session_state.quiz_answers[answer_key]
            
            if selected == correct:
                st.success(f"Question {i+1}: Correct!")
            else:
                st.error(f"Question {i+1}: Incorrect. The correct answer is: {correct}")
    
    if st.button("Download Quiz"):
        quiz_json = json.dumps(quiz_data, indent=2)
        st.download_button(
            label="Download as JSON",
            data=quiz_json,
            file_name="quiz.json",
            mime="application/json"
        )

def render_about_page():
    st.markdown('<h1 class="main-header">About TaskTamer</h1>', unsafe_allow_html=True)
    
    st.write("""
    TaskTamer is a productivity tool designed to help users manage their learning and workflow more effectively. 
    The application combines several powerful features to break down complex tasks, summarize content, and generate 
    quizzes for better knowledge retention.
    """)
    
    st.markdown('<h2 class="section-header">Key Features</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Task Breakdown")
        st.write("Convert complex tasks into manageable, actionable steps")
        
        st.markdown("#### Content Summarization")
        st.write("Extract key insights from text and web pages")
    
    with col2:
        st.markdown("#### Quiz Generation")
        st.write("Create interactive quizzes from any content to test your knowledge")
    
    st.markdown('<h2 class="section-header">About the Developer</h2>', unsafe_allow_html=True)
    
    st.write("""
    TaskTamer was created by **Alessandra Batalha** as part of her final year project at Dublin Business School. 
    The project represents the culmination of her studies in Computer Science, combining practical software 
    engineering skills with artificial intelligence techniques.
    """)
    
    st.write("""
    Alessandra developed TaskTamer with a focus on helping students and professionals manage their learning and 
    work tasks more efficiently. The project demonstrates her skills in full-stack development and user experience design.
    """)
    
    st.markdown(
        '<div class="info-box">'
        '<b>Contact:</b><br>'
        'For more information about this project or to provide feedback, please contact Alessandra Batalha via Dublin Business School.'
        '</div>', 
        unsafe_allow_html=True
    )

def main():
    try:
        # Apply custom styles
        apply_styles()
        
        # Initialize session state
        if "initialized" not in st.session_state:
            st.session_state.initialized = True
            st.session_state.task_data = {}
            st.session_state.quiz_history = []
            st.session_state.chat_history = []
        
        # Sidebar configuration
        st.sidebar.title(APP_TITLE)
        pages = {
            "Home": render_home_page,
            "Task Breakdown": render_task_page,
            "Summarization": render_summary_page,
            "Quiz Generator": render_quiz_page,
            "About": render_about_page
        }
        selection = st.sidebar.radio("Navigate", list(pages.keys()), index=0)
        
        # Main content
        st.sidebar.warning("⚠️ Running in minimal mode. Farm-Haystack not available.")
        st.info(f"{APP_DESCRIPTION}\n\nMade with ❤️ by {DEVELOPER_NAME}")
        st.markdown("---")
        
        # Render selected page
        page_function = pages.get(selection)
        if page_function:
            page_function()
        else:
            st.error("Page not found. Please select a valid page.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        st.write("Please try again or contact support.")

if __name__ == "__main__":
    main()