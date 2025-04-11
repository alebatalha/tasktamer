from typing import List, Dict, Any, Union
import re
import json
from utils.fallback_detector import HAYSTACK_AVAILABLE
from config import MAX_QUIZ_QUESTIONS
from backend.summarization import process_url
from backend.core import tamer

def generate_simple_quiz(content: str, num_questions: int = 3) -> List[Dict[str, Any]]:
    if not content:
        return []
        
    sentences = re.split(r'(?<=[.!?])\s+', content)
    
    selected_sentences = []
    step = max(1, len(sentences) // (num_questions + 1))
    
    for i in range(0, min(len(sentences), num_questions * step), step):
        if i < len(sentences):
            selected_sentences.append(sentences[i])
    
    quiz = []
    
    for i, sentence in enumerate(selected_sentences[:num_questions]):
        words = sentence.split()
        if len(words) < 4:
            continue
            
        word_index = min(len(words) // 2, len(words) - 2)
        correct_word = words[word_index]
        
        incorrect_options = ["Option A", "Option B", "Option C"]
        
        question = " ".join(words[:word_index] + ["_____"] + words[word_index+1:])
        
        quiz.append({
            "question": f"Fill in the blank: {question}",
            "options": [correct_word] + incorrect_options,
            "answer": correct_word
        })
    
    return quiz

def parse_non_json_quiz_format(raw_text: str) -> List[Dict[str, Any]]:
    questions = []
    current_question = {}
    lines = raw_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith("Question") or (current_question and line.endswith("?")):
            if current_question and "question" in current_question and "options" in current_question:
                questions.append(current_question)
            current_question = {"question": line, "options": []}
        elif line.startswith(("A.", "B.", "C.", "D.", "a)", "b)", "c)", "d)")):
            if "options" in current_question:
                option_text = line[2:].strip() if line[1] in [".", ")"] else line
                current_question["options"].append(option_text)
        elif line.startswith("Answer:") or line.startswith("Correct answer:"):
            answer_text = line.split(":", 1)[1].strip()
            option_prefixes = ["A", "B", "C", "D", "a", "b", "c", "d"]
            
            if answer_text in option_prefixes and len(current_question.get("options", [])) > 0:
                idx = option_prefixes.index(answer_text) % 4
                if idx < len(current_question["options"]):
                    current_question["answer"] = current_question["options"][idx]
            else:
                current_question["answer"] = answer_text
    
    if current_question and "question" in current_question and "options" in current_question:
        questions.append(current_question)
    
    return questions

if HAYSTACK_AVAILABLE:
    try:
        from haystack.nodes import PromptNode, PromptTemplate
        from config import LLM_MODEL
        
        quiz_prompt = PromptNode(
            model_name_or_path=LLM_MODEL,
            default_prompt_template=PromptTemplate(
                "Generate {num_questions} multiple-choice questions with one correct answer and three incorrect alternatives from the following text. Format your response as a JSON array with 'question', 'options' (array of 4 strings), and 'answer' (the correct option string) for each question: {documents}"
            )
        )
        
        def generate_quiz(content: str = None, url: str = None, num_questions: int = 3) -> List[Dict[str, Any]]:
            try:
                if num_questions <= 0 or num_questions > MAX_QUIZ_QUESTIONS:
                    num_questions = 3
                
                if url:
                    content = process_url(url)
                
                if not content:
                    return []
                    
                processed_docs = tamer.process_text(content)
                if not processed_docs:
                    return []
                
                response = quiz_prompt(documents=processed_docs, num_questions=num_questions)
                
                if isinstance(response, dict) and "results" in response:
                    try:
                        questions_raw = response["results"][0]
                        if "[" not in questions_raw:
                            questions_raw = f"[{questions_raw}]"
                            
                        questions = json.loads(questions_raw)
                        return questions
                    except json.JSONDecodeError:
                        return parse_non_json_quiz_format(response["results"][0])
                return generate_simple_quiz(content, num_questions)
            except Exception:
                return generate_simple_quiz(content, num_questions)
    except Exception:
        def generate_quiz(content: str = None, url: str = None, num_questions: int = 3) -> List[Dict[str, Any]]:
            if num_questions <= 0 or num_questions > MAX_QUIZ_QUESTIONS:
                num_questions = 3
                
            if url:
                content = process_url(url)
                
            return generate_simple_quiz(content, num_questions)
else:
    def generate_quiz(content: str = None, url: str = None, num_questions: int = 3) -> List[Dict[str, Any]]:
        if num_questions <= 0 or num_questions > MAX_QUIZ_QUESTIONS:
            num_questions = 3
            
        if url:
            content = process_url(url)
            
        return generate_simple_quiz(content, num_questions)