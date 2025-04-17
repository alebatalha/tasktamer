from typing import List
from utils.fallback_detector import HAYSTACK_AVAILABLE

def simple_task_breakdown(task_description: str) -> List[str]:
    if not task_description:
        return []
        
    task_lower = task_description.lower()
    
    if "research" in task_lower:
        return [
            "Define your research topic and goals",
            "Gather relevant sources and materials",
            "Take notes from your sources",
            "Organize your information",
            "Create an outline",
            "Write a first draft",
            "Revise and edit your work"
        ]
    elif "presentation" in task_lower:
        return [
            "Define your presentation topic and audience",
            "Research key information",
            "Create an outline",
            "Design slides or visual aids",
            "Practice your delivery",
            "Get feedback and revise",
            "Finalize your presentation"
        ]
    elif "project" in task_lower:
        return [
            "Define project scope and objectives",
            "Create a timeline with milestones",
            "Identify required resources",
            "Assign responsibilities",
            "Track progress and adjust as needed",
            "Review and quality check",
            "Finalize and deliver"
        ]
    else:
        return [
            "Define your goal and desired outcome",
            "Break down the main components",
            "Create a timeline",
            "Gather necessary resources",
            "Work through each component",
            "Review progress regularly",
            "Complete final review"
        ]

if HAYSTACK_AVAILABLE:
    try:
        from haystack.nodes import PromptNode, PromptTemplate
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
                
            try:
                prompt = f"Break the following task into smaller steps: {task_description}"
                response = task_prompt([prompt])
                
                if isinstance(response, dict) and "results" in response:
                    steps = response["results"][0].split("\n")
                    return [step.strip() for step in steps if step.strip()]
                return simple_task_breakdown(task_description)
            except Exception:
                return simple_task_breakdown(task_description)
    except Exception:
        def break_task(task_description: str) -> List[str]:
            return simple_task_breakdown(task_description)
else:
    def break_task(task_description: str) -> List[str]:
        return simple_task_breakdown(task_description)