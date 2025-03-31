"""
Quiz page UI for TaskTamer.
"""
import streamlit as st
import time
from ..styles import render_header, render_divider, result_container_start, result_container_end
from ..components.inputs import content_input_section

def show_quiz_page(task_tamer):
    """
    Display the quiz interface.
    
    Args:
        task_tamer: TaskTamer instance for backend functionality
    """
    render_header("🧠 Quiz Master", "Create quizzes to test your knowledge")
    
    # Check if we're in quiz taking mode
    if "quiz_questions" in st.session_state and "taking_quiz" in st.session_state and st.session_state.taking_quiz:
        _run_quiz()
        return
    
    # Check if we're showing quiz results
    if "quiz_questions" in st.session_state and not st.session_state.get("taking_quiz", False):
        _display_quiz_results()
        return
    
    # Get content from input section
    content = content_input_section(task_tamer)
    
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

def _run_quiz():
    """Run the quiz interface when in quiz-taking mode."""
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
    render_divider()
    st.write(f"Current score: {st.session_state.quiz_score}/{len(questions)}")

def _display_quiz_results():
    """Display quiz results after completion."""
    result_container_start()
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
    
    result_container_end()
    
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