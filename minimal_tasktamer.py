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