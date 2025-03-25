from typing import Union, List, Dict

try:
    from haystack.nodes import PromptNode, PromptTemplate
except ImportError:
    # Fallback for different haystack versions
    try:
        from haystack.nodes import PromptNode, PromptTemplate
    except ImportError:
        print("Error: Could not import Haystack modules. Please check your installation.")

# Question Generation Prompt
question_prompt = PromptNode(
    model_name_or_path="google/flan-t5-large",
    default_prompt_template=PromptTemplate(
        "Generate a multiple-choice question with one correct answer and three incorrect alternatives from: {documents}"
    )
)

def generate_questions(content: str) -> List[Dict[str, Union[str, List[str]]]]:
    """Generates study questions from provided content.
    
    Args:
        content: Text content to generate questions from
        
    Returns:
        List[Dict]: List of questions with options and answers
    """
    if not content:
        return []
    
    try:
        result = question_prompt(documents=[{"content": content}])
        
        if isinstance(result, dict) and "results" in result:
            # Process the result to extract questions, options, and answers
            # This is a simplified version - you may need to adapt based on actual output format
            questions = []
            raw_questions = result["results"][0].split("\n\n")
            
            for raw_q in raw_questions:
                if not raw_q.strip():
                    continue
                    
                lines = raw_q.strip().split("\n")
                if len(lines) < 5:  # Need at least question and 4 options (3 incorrect + 1 correct)
                    continue
                    
                question = lines[0]
                options = [line.strip()[3:] if line.strip().startswith(('A. ', 'B. ', 'C. ', 'D. ')) 
                           else line.strip() for line in lines[1:5]]
                
                # Assuming the correct answer is noted at the end
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
            
            return questions
            
        return []
    except Exception as e:
        print(f"Error generating questions: {str(e)}")
        return []