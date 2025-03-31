import os
import traceback
from typing import List, Dict, Union, Optional

from .task_manager import TaskManager
from .summarization import Summarizer
from .quiz_generator import QuizGenerator
from .chat_assistant import ChatAssistant

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
        self.advanced_features = ADVANCED_FEATURES
        
        # Initialize modules
        self.task_manager = TaskManager(advanced_features=self.advanced_features)
        self.summarizer = Summarizer(advanced_features=self.advanced_features)
        self.quiz_generator = QuizGenerator(advanced_features=self.advanced_features)
        self.chat_assistant = ChatAssistant()
        
        # Initialize document store if advanced features are available
        self.document_store = None
        self.preprocessor = None
        
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
        except Exception as e:
            print(f"Error initializing advanced features: {str(e)}")
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
        return self.task_manager.break_task(task_description)
    
    def summarize_text(self, content: str) -> str:
        if not content:
          return "No content provided to summarize."
    
    # Call the summarizer's summarize method
          return self.summarizer.summarize(content)
    
    def generate_questions(self, content: str) -> List[Dict[str, Union[str, List[str]]]]:
        """
        Generate study questions from content.
        
        Args:
            content: Text content to generate questions from
            
        Returns:
            List of question dictionaries with questions, options, and answers
        """
        return self.quiz_generator.generate_questions(content)
    
    def get_chat_response(self, prompt: str) -> str:
        """
        Generate a response for the chat assistant.
        
        Args:
            prompt: User's prompt/question
            
        Returns:
            Generated response for the user
        """
        return self.chat_assistant.generate_response(prompt)
    
    def fetch_webpage_content(self, url: str) -> str:
        """
        Fetch and extract text content from a webpage.
        
        Args:
            url: The URL to fetch
            
        Returns:
            Extracted text content
        """
        return self.summarizer.fetch_webpage_content(url)
    
    def process_document(self, content: str) -> str:
        """
        Process document content for analysis.
        
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
    
    def is_advanced_available(self) -> bool:
        """
        Check if advanced features are available.
        
        Returns:
            True if advanced features are available, False otherwise
        """
        return self.advanced_features