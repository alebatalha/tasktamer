# backend/task_breakdown.py
import re
import random
from datetime import datetime, timedelta

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

def suggest_next_action(task_step):
    """
    Suggests a follow-up action for a specific task step.
    This helps users understand what they should do next after completing a step.
    
    Args:
        task_step: The specific task step to suggest an action for
        
    Returns:
        str: A suggested next action
    """
    # List of potential next actions based on common task types
    research_actions = [
        "Find 3-5 credible sources to support this step.",
        "Schedule 30 minutes to search for relevant information.",
        "Contact an expert who might have insights on this topic.",
        "Visit the library or online database to gather resources.",
        "Create a document to store your findings."
    ]
    
    writing_actions = [
        "Create an outline before starting to write.",
        "Set a timer for 25 minutes of focused writing.",
        "Find a quiet place with minimal distractions.",
        "Start with a rough draft, then refine later.",
        "Use tools like Grammarly to help with editing."
    ]
    
    planning_actions = [
        "Set specific deadlines for each component.",
        "Identify potential obstacles and plan for them.",
        "Determine what resources you'll need.",
        "Consider who else needs to be involved.",
        "Create a visual timeline or Gantt chart."
    ]
    
    development_actions = [
        "Break this step into smaller sub-tasks.",
        "Set up the necessary tools or environment first.",
        "Start with a prototype or minimal version.",
        "Schedule regular reviews to ensure you're on track.",
        "Document your process as you go."
    ]
    
    review_actions = [
        "Set specific criteria for what makes this complete.",
        "Ask for feedback from others.",
        "Compare against original requirements.",
        "Take notes on what could be improved.",
        "Create a checklist for final verification."
    ]
    
    general_actions = [
        "Allocate a specific time block to work on this step.",
        "Determine what tools or resources you need to complete this.",
        "Consider if you need help from others for this step.",
        "Set a mini-deadline for completing this step.",
        "Decide how you'll know when this step is complete."
    ]
    
    # Determine which category the task step belongs to
    step_lower = task_step.lower()
    
    if any(term in step_lower for term in ["research", "find", "gather", "collect", "investigate"]):
        action_list = research_actions
    elif any(term in step_lower for term in ["write", "draft", "document", "compose", "create"]):
        action_list = writing_actions
    elif any(term in step_lower for term in ["plan", "schedule", "organize", "arrange", "prepare"]):
        action_list = planning_actions
    elif any(term in step_lower for term in ["develop", "build", "implement", "code", "construct"]):
        action_list = development_actions
    elif any(term in step_lower for term in ["review", "evaluate", "assess", "analyze", "check"]):
        action_list = review_actions
    else:
        action_list = general_actions
    
    # Select a random action from the appropriate list
    suggested_action = random.choice(action_list)
    
    return suggested_action

def create_schedule(steps):
    """
    Creates a simple schedule for completing the task steps.
    
    Args:
        steps: List of task steps
    
    Returns:
        list: A list of dictionaries with step, estimated time, and suggested time slot
    """
    schedule = []
    
    # Very simple scheduling - in a real app, this would be more sophisticated
    time_estimates = {
        "research": "1-2 hours",
        "gather": "30-60 minutes",
        "organize": "30-45 minutes",
        "create": "1-3 hours",
        "write": "1-3 hours",
        "review": "30-60 minutes",
        "prepare": "45-90 minutes",
        "plan": "30-60 minutes",
        "develop": "2-4 hours",
        "finalize": "1 hour",
        "define": "30 minutes",
    }
    
    default_estimate = "45-60 minutes"
    
    # Sample time slots
    time_slots = [
        "Morning (9:00 - 12:00)",
        "Early afternoon (12:00 - 15:00)",
        "Late afternoon (15:00 - 18:00)",
        "Evening (18:00 - 21:00)"
    ]
    
    # Start with today's date
    today = datetime.now()
    current_date = today
    
    for i, step in enumerate(steps):
        # Determine time estimate based on keywords
        estimate = default_estimate
        for keyword, time in time_estimates.items():
            if keyword in step.lower():
                estimate = time
                break
                
        # Suggest a time slot (cycling through options)
        suggested_slot = time_slots[i % len(time_slots)]
        
        # If it's a new day, advance the date
        if i > 0 and i % len(time_slots) == 0:
            current_date += timedelta(days=1)
            
        # Format date
        date_str = current_date.strftime("%A, %b %d")
        
        # Add to schedule
        schedule.append({
            "step": step,
            "estimate": estimate,
            "time_slot": suggested_slot,
            "date": date_str,
            "next_action": suggest_next_action(step)
        })
    
    return schedule