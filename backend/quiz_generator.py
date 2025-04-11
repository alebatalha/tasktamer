from haystack import Pipeline
from haystack.nodes import PromptNode, PromptTemplate
import json
import random
import pandas as pd
import io

# Enhanced Question Generation Prompt
question_prompt = PromptNode(
    model_name_or_path="google/flan-t5-large",
    default_prompt_template=PromptTemplate(
        """Generate a comprehensive quiz based on this content. 
        For each question:
        1. Create a clear, specific question about the key concepts
        2. Provide one correct answer
        3. Create three incorrect but plausible alternative answers
        
        Content: {documents}
        
        Format the response as a JSON array with each question as an object containing 'question', 'correct_answer', and 'incorrect_answers' fields.
        """
    )
)

class QuizManager:
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.score = 0
        self.total_questions = 0
    
    def reset_quiz(self):
        self.questions = []
        self.user_answers = []
        self.score = 0
        self.total_questions = 0
    
    def record_answer(self, question_idx, selected_answer):
        """Record user's answer and update score"""
        if question_idx < len(self.questions):
            correct = selected_answer == self.questions[question_idx]['correct_answer']
            self.user_answers.append({
                'question_idx': question_idx,
                'selected_answer': selected_answer,
                'correct': correct
            })
            if correct:
                self.score += 1
    
    def get_score(self):
        """Return the score as number and percentage"""
        if not self.questions:
            return 0, 0
        
        percentage = (self.score / len(self.questions)) * 100
        return self.score, percentage
    
    def get_feedback(self):
        """Generate feedback based on score percentage"""
        _, percentage = self.get_score()
        
        if percentage >= 90:
            return "Excellent! You have a strong understanding of the material."
        elif percentage >= 75:
            return "Good job! You have a solid grasp of most concepts."
        elif percentage >= 60:
            return "Not bad! You understand the basics but might want to review some areas."
        elif percentage >= 40:
            return "You're making progress! More study is recommended to improve your understanding."
        else:
            return "You should spend more time studying this material to improve your understanding."
    
    def get_download_content(self, format='csv'):
        """Generate downloadable content with questions, options and answers"""
        if not self.questions:
            return None
        
        data = []
        for i, q in enumerate(self.questions):
            all_options = [q['correct_answer']] + q['incorrect_answers']
            random.shuffle(all_options)  # Randomize option order
            
            # Find which option is correct (A, B, C, or D)
            correct_letter = chr(65 + all_options.index(q['correct_answer']))
            
            data.append({
                'Question Number': i + 1,
                'Question': q['question'],
                'Option A': all_options[0],
                'Option B': all_options[1],
                'Option C': all_options[2],
                'Option D': all_options[3],
                'Correct Answer': correct_letter,
                'Correct Answer Text': q['correct_answer']
            })
        
        if format == 'csv':
            df = pd.DataFrame(data)
            csv_buffer = io.StringIO()
            df.to_csv(csv_buffer, index=False)
            return csv_buffer.getvalue()
        
        elif format == 'json':
            return json.dumps(data, indent=2)
        
        elif format == 'text':
            text = "QUIZ QUESTIONS AND ANSWERS\n\n"
            for entry in data:
                text += f"Question {entry['Question Number']}: {entry['Question']}\n"
                text += f"A) {entry['Option A']}\n"
                text += f"B) {entry['Option B']}\n"
                text += f"C) {entry['Option C']}\n"
                text += f"D) {entry['Option D']}\n"
                text += f"Correct Answer: {entry['Correct Answer']} ({entry['Correct Answer Text']})\n\n"
            return text
        
        return None

# Initialize the QuizManager as a global instance
quiz_manager = QuizManager()

def parse_question_response(response):
    """Parse the response from the prompt model into structured questions"""
    try:
        if isinstance(response, dict) and "results" in response:
            # Try to parse as JSON first
            try:
                return json.loads(response["results"][0])
            except json.JSONDecodeError:
                # If not valid JSON, try to extract structured data manually
                questions = []
                raw_text = response["results"][0]
                sections = raw_text.split("\n\n")
                
                current_question = None
                for section in sections:
                    if section.startswith("Question:") or section.startswith("Q:"):
                        # Start a new question
                        if current_question:
                            questions.append(current_question)
                        
                        current_question = {
                            "question": section.split(":", 1)[1].strip(),
                            "correct_answer": "",
                            "incorrect_answers": []
                        }
                    elif section.startswith("Correct answer:") or section.startswith("Correct:"):
                        if current_question:
                            current_question["correct_answer"] = section.split(":", 1)[1].strip()
                    elif section.startswith("Incorrect answers:") or section.startswith("Incorrect:"):
                        if current_question:
                            options = section.split(":", 1)[1].strip().split("\n")
                            current_question["incorrect_answers"] = [opt.strip() for opt in options if opt.strip()]
                
                # Add the last question
                if current_question and current_question["correct_answer"]:
                    questions.append(current_question)
                
                return questions
        
        return []
    except Exception as e:
        print(f"Error parsing question response: {e}")
        return []

def generate_questions(documents, num_questions=10):
    """Generates study questions from documents"""
    global quiz_manager
    
    if not documents:
        return "No document found. Please upload a document or enter content to generate questions."
    
    # Reset the quiz state for new questions
    quiz_manager.reset_quiz()
    
    # Get raw response from the prompt
    response = question_prompt(documents=documents)
    
    # Parse the response into structured questions
    parsed_questions = parse_question_response(response)
    
    # Limit to the requested number of questions
    limited_questions = parsed_questions[:num_questions] if parsed_questions else []
    
    # Store questions in the quiz manager
    quiz_manager.questions = limited_questions
    quiz_manager.total_questions = len(limited_questions)
    
    if not limited_questions:
        # Fallback questions if parsing failed
        return "Failed to generate questions. Please try again with more detailed content."
    
    return limited_questions

def get_formatted_questions():
    """Returns questions formatted for display with randomized options"""
    formatted_questions = []
    
    for idx, question in enumerate(quiz_manager.questions):
        all_options = [question['correct_answer']] + question['incorrect_answers']
        random.shuffle(all_options)  # Randomize option order
        
        formatted_questions.append({
            'question_idx': idx,
            'question': question['question'],
            'options': all_options,
            'correct_answer': question['correct_answer']
        })
    
    return formatted_questions

def record_answer(question_idx, selected_answer):
    """Record the user's answer"""
    global quiz_manager
    quiz_manager.record_answer(question_idx, selected_answer)
    
def get_quiz_results():
    """Get the quiz results and feedback"""
    global quiz_manager
    score, percentage = quiz_manager.get_score()
    feedback = quiz_manager.get_feedback()
    
    return {
        'score': score,
        'total': len(quiz_manager.questions),
        'percentage': percentage,
        'feedback': feedback
    }

def get_quiz_download(format='csv'):
    """Get the quiz content for download"""
    global quiz_manager
    return quiz_manager.get_download_content(format)