from haystack import Pipeline
from haystack.nodes import PromptNode, PromptTemplate

# Question Generation Prompt
question_prompt = PromptNode(
    model_name_or_path="google/flan-t5-large",
    default_prompt_template=PromptTemplate(
        "Generate a multiple-choice question with one correct answer and three incorrect alternatives from: {documents}"
    )
)

def generate_questions(documents):
    """Generates study questions from stored documents."""
    if not documents:
        return "No document found. Please upload a document or enter a webpage URL first."
    return question_prompt(documents=documents)
