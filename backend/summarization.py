# backend/summarization.py
import re

def summarize_documents(text):
    """Creates a simple summary of text without using external AI libraries.
    This is a placeholder that extracts important sentences from the document."""
    if not text or len(text.strip()) < 50:
        return "The provided content is too short to summarize. Please provide more text."
    
    # Simple extractive summarization approach
    # Split text into sentences
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip() and len(s.strip()) > 10]
    
    if not sentences:
        return "Could not extract valid sentences for summarization."
    
    # Score sentences based on simple heuristics
    scored_sentences = []
    for i, sentence in enumerate(sentences):
        score = 0
        
        # Position score - earlier sentences often contain important information
        position_score = 1.0 if i < 3 else 0.5 if i < 5 else 0.3
        score += position_score
        
        # Length score - not too short, not too long
        words = sentence.split()
        length_score = 0.5 if 5 <= len(words) <= 25 else 0.2
        score += length_score
        
        # Keyword score - contains important-sounding words
        important_keywords = ["important", "significant", "key", "main", "critical", "essential", "primary", "major", "crucial"]
        keyword_score = sum(1 for word in words if word.lower() in important_keywords) * 0.5
        score += keyword_score
        
        scored_sentences.append((score, sentence))
    
    # Sort by score and take top sentences
    scored_sentences.sort(reverse=True)
    
    # Determine number of sentences to include in summary (roughly 20-30% of original)
    summary_size = max(3, min(int(len(sentences) * 0.3), 10))
    
    # Get top sentences and sort them by original order
    top_sentences = [s[1] for s in scored_sentences[:summary_size]]
    ordered_sentences = []
    for sentence in sentences:
        if sentence in top_sentences:
            ordered_sentences.append(sentence)
            if len(ordered_sentences) >= summary_size:
                break
    
    # Combine into a summary
    summary = " ".join(ordered_sentences)
    
    # Add a disclaimer
    disclaimer = "\n\n(Note: This is a basic extractive summary. For better results, TaskTamer would use AI-based summarization in a production environment.)"
    
    return summary + disclaimer