import streamlit as st
from backend.task_breakdown import break_task
from backend.summarization import summarize_documents
from backend.question_generation import generate_questions

# Sidebar navigation
st.sidebar.title('TaskTamer')
selection = st.sidebar.radio("Go to", ["Home", "Breakdown Activities", "Summary", "Quiz"])

# Home Page
if selection == "Home":
    st.title('Welcome to TaskTamer')
    st.write('Select a feature from the sidebar to get started.')

# Breakdown Activities Feature
elif selection == "Breakdown Activities":
    st.title('Breakdown Activities')
    task = st.text_input("Enter a complex task:")
    if st.button('Break Down Task'):
        steps = break_task(task)
        if steps:
            st.write("Here are the steps to complete your task:")
            for i, step in enumerate(steps, 1):
                st.write(f"{i}. {step}")
        else:
            st.error("No steps generated.")

# Summary Feature
elif selection == "Summary":
    st.title('Summary')
    content = st.text_area("Enter content to summarize or upload a file:")
    if st.button('Summarize'):
        summary = summarize_documents(content)
        st.write(summary)

# Quiz Feature
elif selection == "Quiz":
    st.title('Quiz')
    if st.button('Generate Quiz'):
        question_data = generate_questions(content)
        if question_data and isinstance(question_data, list) and question_data:
            question = question_data[0]['question']
            options = question_data[0]['options']
            correct_answer = question_data[0]['answer']
            answer = st.radio(question, options)
            if st.button('Submit Answer'):
                if answer == correct_answer:
                    st.success("Correct!")
                else:
                    st.error(f"Incorrect. The correct answer is {correct_answer}.")
        