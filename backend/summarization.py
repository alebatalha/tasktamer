from haystack import Pipeline
from haystack.nodes import PromptNode, PromptTemplate

# Summarization Prompt
summary_prompt = PromptNode(
    model_name_or_path="google/flan-t5-large",
    default_prompt_template=PromptTemplate(
        "Summarize the following document: {documents}"
    )
)

def summarize_documents(documents):
    """Summarizes stored documents."""
    if not documents:
        return "No document found. Please upload a document or enter a webpage URL first."
    return summary_prompt(documents=documents)