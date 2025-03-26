"""
Task management functionality for breaking down complex tasks.
"""
from typing import List, Dict, Any
import traceback

class TaskManager:
    """Handles task breakdown and management."""
    
    def __init__(self, advanced_features: bool = False):
        """
        Initialize the TaskManager.
        
        Args:
            advanced_features: Whether advanced NLP features are available
        """
        self.advanced_features = advanced_features
        self.task_prompt = None
        
        if self.advanced_features:
            self._initialize_advanced_features()
    
    def _initialize_advanced_features(self):
        """Initialize advanced NLP features if available."""
        try:
            from haystack.nodes import PromptNode, PromptTemplate
            
            self.task_prompt = PromptNode(
                model_name_or_path="google/flan-t5-large",
                default_prompt_template=PromptTemplate(
                    "Break the following task into smaller steps: {task_description}"
                )
            )
        except Exception as e:
            print(f"Error initializing task manager advanced features: {str(e)}")
            traceback.print_exc()
            self.advanced_features = False
    
    def break_task(self, task_description: str) -> List[str]:
        """
        Break a task into actionable steps.
        
        Args:
            task_description: The task to break down
            
        Returns:
            List of task steps
        """
        if not task_description:
            return ["Please provide a task to break down."]
        
        # Use advanced features if available
        if self.advanced_features and self.task_prompt:
            try:
                prompt = f"Break the following task into smaller steps: {task_description}"
                response = self.task_prompt([prompt])
                
                if isinstance(response, dict) and "results" in response:
                    steps = [step for step in response["results"][0].split("\n") if step.strip()]
                    if steps:
                        return steps
            except Exception as e:
                print(f"Error using task prompt: {str(e)}")
        
        # Fallback implementation
        return [
            f"1. Understand the goal: {task_description}",
            "2. Research and gather necessary information",
            "3. Break down the task into smaller components",
            "4. Create a timeline with milestones",
            "5. Start with the most important or foundational component",
            "6. Review progress regularly and adjust as needed",
            "7. Complete the final steps and review the outcome"
        ]
    
    def save_task_breakdown(self, task_description: str, steps: List[str]) -> bool:
        """
        Save a task breakdown for later reference.
        
        Args:
            task_description: The original task
            steps: List of task steps
            
        Returns:
            True if save was successful, False otherwise
        """
        # This would save to a database in a real implementation
        # For now, we'll just return True
        return True
    
    def get_saved_tasks(self) -> List[Dict[str, Any]]:
        """
        Get a list of saved task breakdowns.
        
        Returns:
            List of task breakdowns
        """
        # This would retrieve from a database in a real implementation
        return []