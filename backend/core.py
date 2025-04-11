from haystack.document_stores import InMemoryDocumentStore
from haystack.nodes import PreProcessor
from typing import List, Dict, Any, Union
from haystack.nodes import PromptNode

class TaskTamer:
    def __init__(self):
        self.document_store = InMemoryDocumentStore()
        self.preprocessor = PreProcessor(
            clean_empty_lines=True,
            clean_whitespace=True,
            split_by='word',
            split_length=200,
            split_overlap=50,
            split_respect_sentence_boundary=True
        )
        
    def process_text(self, text: str) -> List[Dict[str, Any]]:
        if not text:
            return []
        
        processed_docs = self.preprocessor.process([{"content": text}])
        self.document_store.write_documents(processed_docs)
        return processed_docs
    
    def get_documents(self) -> List[Dict[str, Any]]:
        return self.document_store.get_all_documents()
    
    def clear_documents(self) -> None:
        self.document_store.delete_documents()
        
try:
    from haystack.document_stores import InMemoryDocumentStore
    from haystack.nodes import PreProcessor
    
    class TaskTamer:
        def __init__(self):
            self.document_store = InMemoryDocumentStore()
            self.preprocessor = PreProcessor(
                clean_empty_lines=True,
                clean_whitespace=True,
                split_by='word',
                split_length=200,
                split_overlap=50,
                split_respect_sentence_boundary=True
            )
            
        def process_text(self, text: str) -> List[Dict[str, Any]]:
            if not text:
                return []
            
            processed_docs = self.preprocessor.process([{"content": text}])
            self.document_store.write_documents(processed_docs)
            return processed_docs
        
        def get_documents(self) -> List[Dict[str, Any]]:
            return self.document_store.get_all_documents()
        
        def clear_documents(self) -> None:
            self.document_store.delete_documents()
    
except ImportError:
  
    class TaskTamer:
        def __init__(self):
            self.documents = []
            
        def process_text(self, text: str) -> List[Dict[str, Any]]:
            if not text:
                return []
                
           
            paragraphs = text.split('\n\n')
            processed_docs = []
            
            for i, para in enumerate(paragraphs):
                if para.strip():
                    processed_docs.append({
                        "content": para.strip(),
                        "id": f"doc_{i}"
                    })
                    
            self.documents.extend(processed_docs)
            return processed_docs
            
        def get_documents(self) -> List[Dict[str, Any]]:
            return self.documents
            
        def clear_documents(self) -> None:
            self.documents = []

tamer = TaskTamer()