from haystack.nodes import PromptNode, PromptTemplate
from typing import List
from config import LLM_MODEL

task_prompt = PromptNode(
    model_name_or_path=LLM_MODEL,
    default_prompt_template=PromptTemplate(
        "Break the following task into smaller steps: {task_description}"
    )
)

def break_task(task_description: str) -> List[str]:
    if not task_description:
        return []
        
    prompt = f"Break the following task into smaller steps: {task_description}"
    response = task_prompt([prompt])
    
    if isinstance(response, dict) and "results" in response:
        steps = response["results"][0].split("\n")
        return [step.strip() for step in steps if step.strip()]
    return []