from typing import Union, List, Dict

try:
    from haystack.nodes import PromptNode, PromptTemplate
except ImportError:
    # Fallback for different haystack versions
    try:
        from haystack.nodes import PromptNode, PromptTemplate
    except ImportError:
        print("Error: Could not import Haystack modules. Please check your installation.")

# Summarization Prompt
summary_prompt = PromptNode(
    model_name_or_path="google/flan-t5-large",
    default_prompt_template=PromptTemplate(
        "Summarize the following document: {documents}"
    )
)

def summarize_documents(content: str) -> str:
    """Summarizes the provided text content.
    
    Args:
        content: Text content to summarize
        
    Returns:
        str: Summarized text
    """
    if not content:
        return "No document found. Please upload a document or enter content to summarize."
    
    try:
        result = summary_prompt(documents=[{"content": content}])
        if isinstance(result, dict) and "results" in result:
            return result["results"][0]
        return "Error: No summary generated."
    except Exception as e:
        return f"Error during summarization: {str(e)}"