import os
import re
import sys
import traceback
from typing import List, Dict, Union, Optional, Tuple
import requests
from bs4 import BeautifulSoup

# Flag to track if advanced features are available
ADVANCED_FEATURES = False

try:
    from haystack import Pipeline
    from haystack.nodes import PromptNode, PromptTemplate
    from haystack.document_stores import InMemoryDocumentStore
    from haystack.nodes import PreProcessor, PDFToTextConverter, TextConverter
    ADVANCED_FEATURES = True
except ImportError:
    try:
        from haystack.pipelines import Pipeline
        from haystack.nodes import PromptNode, PromptTemplate
        from haystack.document_stores import InMemoryDocumentStore
        from haystack.nodes import PreProcessor, PDFToTextConverter, TextConverter
        ADVANCED_FEATURES = True
    except ImportError:
        print("Warning: Haystack not available. Using simplified functionality.")


class TaskTamer:
    """Core TaskTamer engine handling all primary functionality."""
    
    def __init__(self):
        """Initialize the TaskTamer with required components."""
        self.document_store = None
        self.preprocessor = None
        self.task_prompt = None
        self.summary_prompt = None
        self.question_prompt = None
        self.advanced_features = ADVANCED_FEATURES
        
        # Initialize advanced features if available
        if self.advanced_features:
            self._initialize_advanced_features()
    
    def _initialize_advanced_features(self):
        """Initialize components that require Haystack."""
        try:
            # Document store for processing documents
            self.document_store = InMemoryDocumentStore()
            
            # Preprocessor for text
            self.preprocessor = PreProcessor(
                clean_empty_lines=True,
                clean_whitespace=True,
                split_by='word',
                split_length=200,
                split_overlap=50,
                split_respect_sentence_boundary=True
            )
            
            # Set up prompts
            self.task_prompt = PromptNode(
                model_name_or_path="google/flan-t5-large",
                default_prompt_template=PromptTemplate(
                    "Break the following task into smaller steps: {task_description}"
                )
            )
            
            self.summary_prompt = PromptNode(
                model_name_or_path="google/flan-t5-large",
                default_prompt_template=PromptTemplate(
                    "Summarize the following document: {documents}"
                )
            )
            
            self.question_prompt = PromptNode(
                model_name_or_path="google/flan-t5-large",
                default_prompt_template=PromptTemplate(
                    "Generate a multiple-choice question with one correct answer and three incorrect alternatives from: {documents}"
                )
            )
        except Exception as e:
            print(f"Error initializing advanced features: {str(e)}")
            traceback.print_exc()
            self.advanced_features = False
    
    def break_task(self, task_description: str) -> List[str]:
        """Break a task into actionable steps.
        
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
    
    def fetch_webpage_content(self, url: str) -> str:
        """Fetch and extract text content from a webpage.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Extracted text content
        """
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            paragraphs = soup.find_all("p")
            text = "\n".join([p.get_text() for p in paragraphs])
            return text if text else "No readable content found."
        except requests.RequestException as e:
            return f"Error fetching webpage: {e}"
    
    def process_document(self, content: str) -> str:
        """Process document content for analysis.
        
        Args:
            content: Text content to process
            
        Returns:
            Processed content
        """
        if not content:
            return ""
            
        if self.advanced_features and self.preprocessor and self.document_store:
            try:
                processed_docs = self.preprocessor.process([{"content": content}])
                self.document_store.write_documents(processed_docs)
                return content
            except Exception as e:
                print(f"Error processing document: {str(e)}")
        
        # Return original content if processing fails
        return content
    
    def summarize_text(self, content: str) -> str:
        """Generate a summary of the provided text.
        
        Args:
            content: Text content to summarize
            
        Returns:
            Summary text
        """
        if not content:
            return "No content provided to summarize."
            
        # Use advanced features if available
        if self.advanced_features and self.summary_prompt:
            try:
                result = self.summary_prompt(documents=[{"content": content}])
                if isinstance(result, dict) and "results" in result:
                    return result["results"][0]
            except Exception as e:
                print(f"Error using summary prompt: {str(e)}")
        
        # Fallback simple summarization
        sentences = content.split('. ')
        if len(sentences) <= 3:
            return content
            
        # Simple summary with first and last sentences
        summary = '. '.join([sentences[0], sentences[1]])
        if len(sentences) > 3:
            summary += '. ' + sentences[-2] + '. ' + sentences[-1]
        return summary
    
    def generate_questions(self, content: str) -> List[Dict[str, Union[str, List[str]]]]:
        """Generate study questions from content.
        
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
        """Generate fallback questions when advanced features are unavailable.
        
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
    
    def is_advanced_available(self) -> bool:
        """Check if advanced features are available.
        
        Returns:
            True if advanced features are available, False otherwise
        """
        return self.advanced_features