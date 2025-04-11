from typing import List
from utils.fallback_detector import USING_FALLBACK

if not USING_FALLBACK:
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
                
            prompt = f"Break the following task into smaller steps: {task_description}"
            response = task_prompt([prompt])
            
            if isinstance(response, dict) and "results" in response:
                steps = response["results"][0].split("\n")
                return [step.strip() for step in steps if step.strip()]
            return []
    except Exception:
        
        USING_FALLBACK = True


if USING_FALLBACK:
    def break_task(task_description: str) -> List[str]:
        """Breaks a task into actionable steps using rule-based approach."""
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
            # Generic task breakdown
            return [
                "Define your goal and desired outcome",
                "Break down the main components",
                "Create a timeline",
                "Gather necessary resources",
                "Work through each component",
                "Review progress regularly",
                "Complete final review"
            ]