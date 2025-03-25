from haystack import Pipeline
from haystack.nodes import PromptNode, PromptTemplate

# Task Breakdown Prompt
task_breakdown_prompt = PromptNode(
    model_name_or_path="google/flan-t5-large",
    default_prompt_template=PromptTemplate(
        "Break the following task into smaller steps: {task_description}"
    )
)

def break_task(task_description: str):
    """Breaks a task into actionable steps."""
    prompt = f"Break the following task into smaller steps: {task_description}"
    response = task_breakdown_prompt([prompt])  # Pass a list of strings

    if isinstance(response, dict) and "results" in response:
        return response["results"][0].split("\n")
    return ["Error: No response received."]