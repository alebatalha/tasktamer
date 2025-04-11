import streamlit as st
from backend.quiz_generator import generate_quiz
from ui.styles import main_header, section_header, warning_box, success_box
import re
import json

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

def render_quiz_page():
    main_header("Quiz Generator")
    
    st.write("Create quizzes from text, web pages, or YouTube videos")
    
    tab1, tab2 = st.tabs(["Text Input", "URL"])
    
    with tab1:
        text_content = st.text_area(
            "Enter the content you want to create a quiz from:", 
            height=200,
            help="Paste the text you want to create a quiz from"
        )
        
        num_questions = st.slider("Number of questions", 1, 10, 3)
        
        if st.button("Generate Quiz", key="text_quiz_btn"):
            if not text_content:
                warning_box("Please enter some text to generate a quiz from")
                return
                
            with st.spinner("Generating quiz..."):
                quiz = generate_quiz(content=text_content, num_questions=num_questions)
                
            display_quiz(quiz)
    
    with tab2:
        url = st.text_input(
            "Enter a webpage or YouTube URL:",
            help="Works with most websites and YouTube videos"
        )
        
        num_questions = st.slider("Number of questions", 1, 10, 3, key="url_num_q")
        
        if st.button("Generate Quiz", key="url_quiz_btn"):
            if not url:
                warning_box("Please enter a URL")
                return
                
            if not is_valid_url(url):
                warning_box("Please enter a valid URL")
                return
                
            with st.spinner("Fetching content and generating quiz..."):
                quiz = generate_quiz(url=url, num_questions=num_questions)
                
            display_quiz(quiz)

def display_quiz(quiz_data):
    if not quiz_data:
        warning_box("Could not generate quiz. Please try with different content.")
        return
        
    section_header("Your Quiz")
    
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
            
            selected = st.radio(
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
        success_box(f"Your score: {st.session_state.quiz_score}/{len(quiz_data)} ({score_percentage:.1f}%)")
        
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