# backend/task_breakdown.py
import re

def break_task(task_description):
    """Breaks a task into actionable steps without using external libraries."""
    if not task_description or len(task_description.strip()) < 10:
        return ["Please provide a more detailed task description."]
    
    # Simple rule-based task breakdown
    # In a real application, this would use AI models
    steps = []
    
    # Split by sentences or conjunctions as potential step boundaries
    segments = re.split(r'(?<=[.!?])\s+|\s+and\s+|\s*,\s*|\s+then\s+', task_description)
    segments = [s.strip() for s in segments if s.strip()]
    
    # Convert segments to action steps
    for i, segment in enumerate(segments):
        # Skip very short segments
        if len(segment) < 5:
            continue
            
        # Add action verbs to the beginning if not present
        if not any(segment.lower().startswith(verb) for verb in ["identify", "create", "plan", "research", "review", "write", "develop", "organize", "prepare", "analyze"]):
            action_verb = "Prepare" if i == 0 else "Develop" if i == 1 else "Review" if i == 2 else "Finalize"
            step = f"{action_verb} {segment}"
        else:
            # Capitalize first letter
            step = segment[0].upper() + segment[1:]
            
        # Ensure it ends with proper punctuation
        if not step.endswith((".", "!", "?")):
            step += "."
            
        steps.append(step)
    
    # If we couldn't extract meaningful steps, provide generic ones
    if len(steps) < 2:
        task_type = "research" if any(word in task_description.lower() for word in ["research", "study", "learn", "analyze"]) else "task"
        
        if task_type == "research":
            steps = [
                f"Research the topic: {task_description}",
                "Gather key information and resources.",
                "Organize your findings into main categories.",
                "Create an outline based on your research.",
                "Prepare the final document or presentation."
            ]
        else:
            steps = [
                f"Define the scope and objectives for: {task_description}",
                "Break down the main components needed.",
                "Assign priorities to each component.",
                "Create a timeline for completion.",
                "Execute the plan and track progress."
            ]
    
    return steps