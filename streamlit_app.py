import streamlit as st
from ui.pages.home_page import render_home_page
from ui.pages.task_page import render_task_page
from ui.pages.summary_page import render_summary_page
from ui.pages.quiz_page import render_quiz_page
from ui.pages.about_page import render_about_page
from ui.styles import apply_styles

def main():
    try:
        apply_styles()


        st.sidebar.title("TaskTamer")
        pages = {
            "Home": render_home_page,
            "Task Breakdown": render_task_page,
            "Summarization": render_summary_page,
            "Quiz Generator": render_quiz_page,
            "About": render_about_page
        }

        selection = st.sidebar.radio("Navigate", list(pages.keys()), index=0)

        st.info(
            "**TaskTamer** helps you manage complex tasks, "
            "summarize content, and test your knowledge. "
            "Made with ❤️ by Alessandra Batalha"
        )
        st.markdown("---")

        page_function = pages.get(selection)
        if page_function:
            page_function()
        else:
            st.error("Selected page not found.")

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()