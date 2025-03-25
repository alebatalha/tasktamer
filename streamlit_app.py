import streamlit as st
import os
import sys

# Ensure the backend directory is in the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import backend functions
from backend.task_breakdown import break_task
from backend.summarization import summarize_documents
from backend.question_generation import generate_questions

# App title and description
st.set_page_config(
    page_title="TaskTamer",
    page_icon="📝",
    layout="wide"
)

# Sidebar navigation
st.sidebar.title('TaskTamer')
st.sidebar.subheader('Your productivity assistant')
selection = st.sidebar.radio("Go to", ["Home", "Breakdown Activities", "Summary", "Quiz"])

# Home Page
if selection == "Home":
    st.title('Welcome to TaskTamer')
    st.write('TaskTamer helps you break down complex tasks, summarize documents, and create quizzes to test your knowledge.')
    st.write('Select a feature from the sidebar to get started.')
    
    # Feature cards
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("### 📋 Task Breakdown")
        st.markdown("Break complex tasks into manageable steps")
        
    with col2:
        st.markdown("### 📑 Summary")
        st.markdown("Generate concise summaries of your documents")
        
    with col3:
        st.markdown("### 🧠 Quiz")
        st.markdown("Test your understanding with auto-generated questions")

# Breakdown Activities Feature
elif selection == "Breakdown Activities":
    st.title('Breakdown Activities')
    st.write('Enter a complex task and we\'ll break it down into manageable steps.')
    
    task = st.text_area("Enter a complex task:", height=100, 
                         placeholder="Example: Write a research paper on climate change")
    
    if st.button('Break Down Task'):
        with st.spinner('Breaking down task...'):
            steps = break_task(task)
            
        if steps and len(steps) > 1:
            st.write("Here are the steps to complete your task:")
            for i, step in enumerate(steps, 1):
                if step.strip():  # Only show non-empty steps
                    st.write(f"{i}. {step}")
                    # Add checkbox for each step
                    st.checkbox(f"Mark step {i} as complete", key=f"step_{i}")
        else:
            st.error("Could not generate steps. Please try a different task description.")

# Summary Feature
elif selection == "Summary":
    st.title('Document Summary')
    st.write('Enter text or upload a document to generate a concise summary.')
    
    # File upload option
    uploaded_file = st.file_uploader("Upload a document (optional)", type=['txt', 'pdf'])
    
    # Text input option
    content = st.text_area("Or enter text to summarize:", height=200)
    
    # Handle the uploaded file
    if uploaded_file is not None:
        # Save the file temporarily
        with open("temp_file.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Read the file content
        with open("temp_file.txt", "r") as f:
            content = f.read()
    
    if st.button('Generate Summary'):
        if not content:
            st.error("Please provide some text or upload a document to summarize.")
        else:
            with st.spinner('Generating summary...'):
                summary = summarize_documents(content)
            
            st.subheader("Summary")
            st.write(summary)
            
            # Option to save the summary
            if st.button('Save Summary'):
                st.download_button(
                    label="Download Summary",
                    data=summary,
                    file_name="summary.txt",
                    mime="text/plain"
                )

# Quiz Feature
elif selection == "Quiz":
    st.title('Knowledge Quiz')
    st.write('Generate quiz questions from your study materials to test your understanding.')
    
    # File upload option
    uploaded_file = st.file_uploader("Upload a document (optional)", type=['txt', 'pdf'])
    
    # Text input option
    content = st.text_area("Or enter text to generate questions from:", height=200)
    
    # Handle the uploaded file
    if uploaded_file is not None:
        # Save the file temporarily
        with open("temp_file.txt", "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        # Read the file content
        with open("temp_file.txt", "r") as f:
            content = f.read()
    
    if st.button('Generate Quiz'):
        if not content:
            st.error("Please provide some text or upload a document to generate questions from.")
        else:
            with st.spinner('Generating questions...'):
                questions = generate_questions(content)
            
            if questions:
                st.session_state.questions = questions
                st.session_state.current_question = 0
                st.session_state.score = 0
                st.session_state.total = len(questions)
                st.rerun()
            else:
                st.error("Could not generate questions. Please try different content.")
    
    # Display quiz
    if 'questions' in st.session_state and st.session_state.questions:
        if 'current_question' not in st.session_state:
            st.session_state.current_question = 0
            
        if 'answered' not in st.session_state:
            st.session_state.answered = False
            
        current_q = st.session_state.current_question
        question_data = st.session_state.questions[current_q]
        
        st.subheader(f"Question {current_q + 1}/{st.session_state.total}")
        st.write(question_data['question'])
        
        # Display options
        answer = st.radio("Select your answer:", question_data['options'], key=f"q_{current_q}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button('Submit Answer'):
                st.session_state.answered = True
                
                if answer == question_data['answer']:
                    st.success("Correct! ✅")
                    if not st.session_state.get(f"answered_{current_q}", False):
                        st.session_state.score += 1
                        st.session_state[f"answered_{current_q}"] = True
                else:
                    st.error(f"Incorrect. The correct answer is: {question_data['answer']}")
                    st.session_state[f"answered_{current_q}"] = True
        
        with col2:
            if st.button('Next Question'):
                if current_q < len(st.session_state.questions) - 1:
                    st.session_state.current_question += 1
                    st.session_state.answered = False
                    st.rerun()
                else:
                    st.info(f"Quiz completed! Your score: {st.session_state.score}/{st.session_state.total}")
                    if st.button('Restart Quiz'):
                        st.session_state.current_question = 0
                        st.session_state.score = 0
                        st.session_state.answered = False
                        st.rerun()