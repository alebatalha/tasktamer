"""
Quiz generation functionality for TaskTamer.
"""
import re
import traceback
from typing import List, Dict, Union, Any

class QuizGenerator:
    """Handles quiz generation and management."""
    
    def __init__(self, advanced_features: bool = False):
        """
        Initialize the QuizGenerator.
        
        Args:
            advanced_features: Whether advanced NLP features are available
        """
        self.advanced_features = advanced_features
        self.question_prompt = None
        
        if self.advanced_features:
            self._initialize_advanced_features()
    
    def _initialize_advanced_features(self):
        """Initialize advanced NLP features if available."""
        try:
            from haystack.nodes import PromptNode, PromptTemplate
            
            self.question_prompt = PromptNode(
                model_name_or_path="google/flan-t5-large",
                default_prompt_template=PromptTemplate(
                    "Generate a multiple-choice question with one correct answer and three incorrect alternatives from: {documents}"
                )
            )
        except Exception as e:
            print(f"Error initializing quiz generator advanced features: {str(e)}")
            traceback.print_exc()
            self.advanced_features = False
    
    def generate_questions(self, content: str) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Generate study questions from content.
        
        Args:
            content: Text content to generate questions from
            
        Returns:
            List of question dictionaries with questions, options, and answers
        """
        if not content:
            return []
            
        # Use advanced features if available
        if self.advanced_features and self.question_prompt:
            try:
                result = self.question_prompt(documents=[{"content": content}])
                
                if isinstance(result, dict) and "results" in result:
                    questions = []
                    raw_questions = result["results"][0].split("\n\n")
                    
                    for raw_q in raw_questions:
                        if not raw_q.strip():
                            continue
                            
                        lines = raw_q.strip().split("\n")
                        if len(lines) < 5:  # Need question and options
                            continue
                            
                        question = lines[0]
                        options = [line.strip()[3:] if line.strip().startswith(('A. ', 'B. ', 'C. ', 'D. ')) 
                                   else line.strip() for line in lines[1:5]]
                        
                        # Determine correct answer
                        correct_index = 0  # Default to first option
                        for i, line in enumerate(lines):
                            if "correct" in line.lower():
                                for opt in "ABCD":
                                    if opt in line:
                                        correct_index = "ABCD".index(opt)
                                        break
                        
                        questions.append({
                            "question": question,
                            "options": options,
                            "answer": options[correct_index]
                        })
                    
                    if questions:
                        return questions
            except Exception as e:
                print(f"Error generating questions: {str(e)}")
        
        # Fallback question generation
        return self._generate_fallback_questions(content)
    
    def _generate_fallback_questions(self, content: str) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Generate fallback questions when advanced features are unavailable.
        
        Args:
            content: Text content to generate questions from
            
        Returns:
            List of generated questions
        """
        # Extract important terms
        words = re.findall(r'\b[A-Za-z][a-z]{5,}\b', content)
        if not words:
            topic = "this topic"
        else:
            # Use most common substantive word
            word_counts = {}
            for word in words:
                word_counts[word.lower()] = word_counts.get(word.lower(), 0) + 1
            
            # Sort by frequency
            common_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
            topic = common_words[0][0] if common_words else "this topic"
        
        # Create questions using the identified topic
        return [
            {
                "question": f"Which of the following best describes {topic}?",
                "options": [
                    f"A fundamental concept in the field",
                    f"A complex system with multiple components",
                    f"A recent innovation in technology",
                    f"A theoretical framework for analysis"
                ],
                "answer": "A fundamental concept in the field"
            },
            {
                "question": f"What is the primary purpose of studying {topic}?",
                "options": [
                    "To develop practical applications",
                    "To understand theoretical foundations",
                    "To analyze historical developments",
                    "To predict future trends"
                ],
                "answer": "To understand theoretical foundations"
            }
        ]
    
    def save_quiz(self, questions: List[Dict[str, Any]], title: str = "") -> bool:
        """
        Save a quiz for later reference.
        
        Args:
            questions: List of quiz questions
            title: Optional title for the quiz
            
        Returns:
            True if save was successful, False otherwise
        """
        # This would save to a database in a real implementation
        # For now, we'll just return True
        return True
    
    def grade_quiz(self, questions: List[Dict[str, Any]], answers: List[str]) -> Dict[str, Any]:
        """
        Grade a completed quiz.
        
        Args:
            questions: List of quiz questions
            answers: List of user answers
            
        Returns:
            Quiz results with score and feedback
        """
        if len(questions) != len(answers):
            return {"error": "Number of answers does not match number of questions"}
        
        correct_count = 0
        question_results = []
        
        for i, (question, answer) in enumerate(zip(questions, answers)):
            is_correct = answer == question["answer"]
            if is_correct:
                correct_count += 1
            
            question_results.append({
                "question_number": i + 1,
                "question_text": question["question"],
                "user_answer": answer,
                "correct_answer": question["answer"],
                "is_correct": is_correct
            })
        
        score_percentage = (correct_count / len(questions)) * 100 if questions else 0
        
        return {
            "total_questions": len(questions),
            "correct_answers": correct_count,
            "score_percentage": score_percentage,
            "question_results": question_results
        }