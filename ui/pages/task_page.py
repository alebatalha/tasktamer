"""
Task breakdown page UI for TaskTamer.
"""
import streamlit as st
import time
from ..styles import render_header, render_divider, result_container_start, result_container_end

def show_task_page(task_tamer):
    """
    Display the task breakdown interface.
    
    Args:
        task_tamer: TaskTamer instance for backend functionality
    """
    render_header("📋 Task Breaker", "Break complex tasks into manageable steps")
    
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
        _display_task_steps(st.session_state.task_steps)

def _display_task_steps(steps):
    """
    Display the task steps with checkboxes.
    
    Args:
        steps: List of task steps to display
    """
    result_container_start()
    st.markdown("### Here's your task breakdown:")
    
    for i, step in enumerate(steps, 1):
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
    
    result_container_end()
    
    # Add options to save or share
    render_divider()
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Save as Text"):
            steps_text = "\n".join([f"{i+1}. {step}" for i, step in enumerate(steps)])
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