import streamlit as st
from backend.task_manager import break_task
from ui.styles import main_header, task_item, section_header, warning_box

def render_task_page():
    main_header("Task Breakdown")
    
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
            warning_box("Please enter a task description")
            return
            
        with st.spinner("Breaking down your task..."):
            steps = break_task(task_description)
            
        if steps:
            section_header("Here's your task breakdown:")
            
            for i, step in enumerate(steps, 1):
                task_item(step, i)
                
            st.download_button(
                label="Download Task Breakdown",
                data="\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)]),
                file_name="task_breakdown.txt",
                mime="text/plain"
            )
        else:
            warning_box("Could not generate steps. Please try rewording your task.")