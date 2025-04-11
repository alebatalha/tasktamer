import streamlit as st
import os
import tempfile
from backend.task_breakdown import break_task
from backend.summarization import summarize_documents
from backend.question_generation import (
    generate_questions, 
    get_formatted_questions, 
    record_answer, 
    get_quiz_results, 
    get_quiz_download
)

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

# Sidebar navigation
st.sidebar.title('TaskTamer')
selection = st.sidebar.radio("Go to", ["Home", "Breakdown Activities", "Summary", "Quiz"])

# Home Page
if selection == "Home":
    st.title('Welcome to TaskTamer')
    st.write('TaskTamer helps you break down complex tasks, summarize documents, and test your knowledge with quizzes.')
    st.write('Select a feature from the sidebar to get started.')

# Breakdown Activities Feature
elif selection == "Breakdown Activities":
    st.title('Breakdown Activities')
    task = st.text_input("Enter a complex task:")
    if st.button('Break Down Task'):
        with st.spinner('Breaking down your task...'):
            steps = break_task(task)
            if steps:
                st.write("Here are the steps to complete your task:")
                for i, step in enumerate(steps, 1):
                    st.write(f"{i}. {step}")
            else:
                st.error("No steps generated.")

# Summary Feature
elif selection == "Summary":
    st.title('Document Summary')
    
    content_option = st.radio("Choose content source:", ["Text Input", "File Upload"])
    
    if content_option == "Text Input":
        text_content = st.text_area("Enter content to summarize:", height=250)
        if st.button('Summarize Text'):
            if text_content:
                st.session_state.content = text_content
                with st.spinner('Generating summary...'):
                    summary = summarize_documents(text_content)
                    st.subheader("Summary")
                    st.write(summary)
            else:
                st.warning("Please enter some text to summarize.")
    
    else:  # File Upload
        uploaded_file = st.file_uploader("Upload a document:", type=['txt', 'pdf', 'docx'])
        if uploaded_file is not None:
            if st.button('Summarize File'):
                with st.spinner('Processing file and generating summary...'):
                    file_content = read_file_content(uploaded_file)
                    st.session_state.content = file_content
                    summary = summarize_documents(file_content)
                    st.subheader("Summary")
                    st.write(summary)

# Quiz Feature
elif selection == "Quiz":
    st.title('Knowledge Quiz')
    
    if not st.session_state.quiz_started:
        content_option = st.radio("Choose content source:", ["Text Input", "File Upload"])
        
        if content_option == "Text Input":
            text_content = st.text_area("Enter content to create a quiz from:", height=250)
            num_questions = st.slider("Number of questions:", min_value=1, max_value=10, value=5)
            if st.button('Generate Quiz from Text'):
                if text_content:
                    with st.spinner('Generating quiz questions...'):
                        st.session_state.content = text_content
                        questions = generate_questions(text_content, num_questions)
                        if questions:
                            st.session_state.formatted_questions = get_formatted_questions()
                            start_quiz()
                        else:
                            st.error("Failed to generate questions. Please provide more detailed content.")
                else:
                    st.warning("Please enter some text first.")
        
        else:  # File Upload
            uploaded_file = st.file_uploader("Upload a document:", type=['txt', 'pdf', 'docx'])
            num_questions = st.slider("Number of questions:", min_value=1, max_value=10, value=5)
            if uploaded_file is not None:
                if st.button('Generate Quiz from File'):
                    with st.spinner('Processing file and generating quiz...'):
                        file_content = read_file_content(uploaded_file)
                        st.session_state.content = file_content
                        questions = generate_questions(file_content, num_questions)
                        if questions:
                            st.session_state.formatted_questions = get_formatted_questions()
                            start_quiz()
                        else:
                            st.error("Failed to generate questions. Please provide more detailed content.")
    
    # Display quiz if started
    elif st.session_state.quiz_started and not st.session_state.quiz_complete:
        questions = st.session_state.formatted_questions
        if questions and st.session_state.current_question < len(questions):
            current_q = questions[st.session_state.current_question]
            
            # Progress indicator
            st.progress((st.session_state.current_question) / len(questions))
            st.write(f"Question {st.session_state.current_question + 1} of {len(questions)}")
            
            # Display question
            st.subheader(current_q['question'])
            
            # Create radio buttons for options
            answer = st.radio(
                "Select your answer:",
                current_q['options'],
                key=f"q_{st.session_state.current_question}"
            )
            
            # Next button
            if st.button('Submit Answer'):
                # Record the answer
                record_answer(current_q['question_idx'], answer)
                next_question()
                st.rerun()
    
    # Show results when quiz is complete
    if st.session_state.quiz_complete:
        results = get_quiz_results()
        
        st.success(f"Quiz Complete! Your score: {results['score']}/{results['total']} ({results['percentage']:.1f}%)")
        st.info(results['feedback'])
        
        # Display all questions with correct/incorrect answers
        st.subheader("Review Questions")
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
        st.subheader("Download Quiz")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            csv_data = get_quiz_download(format='csv')
            st.download_button(
                label="Download CSV",
                data=csv_data,
                file_name="task_tamer_quiz.csv",
                mime="text/csv"
            )
        
        with col2:
            json_data = get_quiz_download(format='json')
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name="task_tamer_quiz.json",
                mime="application/json"
            )
        
        with col3:
            text_data = get_quiz_download(format='text')
            st.download_button(
                label="Download Text",
                data=text_data,
                file_name="task_tamer_quiz.txt",
                mime="text/plain"
            )
        
        # Option to restart
        if st.button("Start New Quiz"):
            reset_quiz()
            st.rerun()