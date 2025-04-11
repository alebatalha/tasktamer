# backend/question_generation.py
import random
import json
import io
import csv
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

# Simplified version that doesn't rely on haystack's advanced features
class QuizGenerator:
    def __init__(self):
        self.questions = []
        self.user_answers = []
        self.score = 0
        self.total_questions = 0
    
    def reset_quiz(self):
        """Reset the quiz state"""
        self.questions = []
        self.user_answers = []
        self.score = 0
        self.total_questions = 0
    
    def record_answer(self, question_idx, selected_answer):
        """Record user's answer and update score"""
        if question_idx < len(self.questions):
            question = self.questions[question_idx]
            is_correct = selected_answer == question['correct_answer']
            
            self.user_answers.append({
                'question_idx': question_idx,
                'selected_answer': selected_answer,
                'is_correct': is_correct
            })
            
            if is_correct:
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
        
        if format == 'csv':
            output = io.StringIO()
            writer = csv.writer(output)
            
            # Write header
            writer.writerow(['Question Number', 'Question', 'Option A', 'Option B', 
                            'Option C', 'Option D', 'Correct Answer', 'Correct Answer Text'])
            
            # Write data
            for i, q in enumerate(self.questions):
                all_options = [q['correct_answer']] + q['incorrect_answers']
                random.shuffle(all_options)  # Randomize option order
                
                # Find which option is correct (A, B, C, or D)
                correct_letter = chr(65 + all_options.index(q['correct_answer']))
                
                writer.writerow([
                    i + 1,
                    q['question'],
                    all_options[0],
                    all_options[1],
                    all_options[2],
                    all_options[3],
                    correct_letter,
                    q['correct_answer']
                ])
            
            return output.getvalue()
        
        elif format == 'json':
            data = []
            for i, q in enumerate(self.questions):
                all_options = [q['correct_answer']] + q['incorrect_answers']
                random.shuffle(all_options)  # Randomize option order
                
                # Find which option is correct (A, B, C, or D)
                correct_letter = chr(65 + all_options.index(q['correct_answer']))
                
                data.append({
                    'question_number': i + 1,
                    'question': q['question'],
                    'options': {
                        'A': all_options[0],
                        'B': all_options[1],
                        'C': all_options[2],
                        'D': all_options[3]
                    },
                    'correct_answer': correct_letter,
                    'correct_answer_text': q['correct_answer']
                })
            
            return json.dumps(data, indent=2)
        
        elif format == 'text':
            text = "QUIZ QUESTIONS AND ANSWERS\n\n"
            for i, q in enumerate(self.questions):
                all_options = [q['correct_answer']] + q['incorrect_answers']
                random.shuffle(all_options)  # Randomize option order
                
                # Find which option is correct (A, B, C, or D)
                correct_letter = chr(65 + all_options.index(q['correct_answer']))
                
                text += f"Question {i+1}: {q['question']}\n"
                text += f"A) {all_options[0]}\n"
                text += f"B) {all_options[1]}\n"
                text += f"C) {all_options[2]}\n"
                text += f"D) {all_options[3]}\n"
                text += f"Correct Answer: {correct_letter} ({q['correct_answer']})\n\n"
            
            return text
        
        return None

# Create a global instance of QuizGenerator
quiz_generator = QuizGenerator()

# Example questions for testing (fallback if AI generation fails)
SAMPLE_QUESTIONS = [
    {
        "question": "What is the primary purpose of TaskTamer?",
        "correct_answer": "To break down complex tasks into manageable steps",
        "incorrect_answers": [
            "To manage project deadlines",
            "To assign tasks to team members",
            "To track time spent on tasks"
        ]
    },
    {
        "question": "Which feature helps test your understanding of content?",
        "correct_answer": "Quiz",
        "incorrect_answers": [
            "Breakdown",
            "Summary",
            "Timeline"
        ]
    },
    {
        "question": "What is the main benefit of breaking down tasks?",
        "correct_answer": "It makes complex tasks more manageable",
        "incorrect_answers": [
            "It automatically completes the tasks for you",
            "It creates a visual timeline",
            "It assigns tasks to team members"
        ]
    },
    {
        "question": "How does TaskTamer help with learning?",
        "correct_answer": "By creating quizzes to test your understanding",
        "incorrect_answers": [
            "By automatically completing research for you",
            "By connecting you with tutors",
            "By providing pre-written essays"
        ]
    },
    {
        "question": "Which of these is NOT a feature of TaskTamer?",
        "correct_answer": "Video conferencing with team members",
        "incorrect_answers": [
            "Task breakdown",
            "Document summarization",
            "Knowledge quizzes"
        ]
    }
]

def fetch_webpage_content(url):
    """Fetches and extracts text content from a web page or YouTube video."""
    try:
        # Check if it's a YouTube URL
        if is_youtube_url(url):
            return fetch_youtube_captions(url)
            
        # Otherwise treat it as a regular webpage
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Remove script and style elements
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.extract()
        
        # Get text content from paragraphs, headings, and lists
        paragraphs = soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'li'])
        text = "\n".join([elem.get_text().strip() for elem in paragraphs if elem.get_text().strip()])
        
        if not text:
            # If no structured elements found, get all text
            text = soup.get_text()
            # Clean up whitespace
            text = re.sub(r'\s+', ' ', text).strip()
        
        return text if text else "No readable content found."
    except requests.RequestException as e:
        return f"Error fetching webpage: {str(e)}"
    except Exception as e:
        return f"Error processing webpage: {str(e)}"

def is_youtube_url(url):
    """Check if a URL is a YouTube video."""
    parsed_url = urlparse(url)
    
    # Standard YouTube URLs
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com') and parsed_url.path == '/watch':
        return True
    
    # YouTube Shorts
    if parsed_url.netloc in ('youtube.com', 'www.youtube.com') and '/shorts/' in parsed_url.path:
        return True
    
    # Shortened youtu.be links
    if parsed_url.netloc == 'youtu.be':
        return True
    
    return False

def fetch_youtube_captions(url):
    """
    Attempt to fetch captions/transcripts from a YouTube video.
    
    This is a simplified version. In a production app, you would:
    1. Use the YouTube Data API
    2. Or use a library like youtube-transcript-api
    
    This function simulates getting transcripts by returning a placeholder message
    """
    try:
        # Extract video ID
        video_id = None
        parsed_url = urlparse(url)
        
        if parsed_url.netloc in ('youtube.com', 'www.youtube.com'):
            if parsed_url.path == '/watch':
                # Regular YouTube URL
                query = parse_qs(parsed_url.query)
                video_id = query.get('v', [''])[0]
            elif '/shorts/' in parsed_url.path:
                # YouTube Shorts
                video_id = parsed_url.path.split('/shorts/')[1]
        elif parsed_url.netloc == 'youtu.be':
            # Shortened URL
            video_id = parsed_url.path.lstrip('/')
        
        if not video_id:
            return "Could not extract YouTube video ID from URL."
        
        # In a real implementation, you would call YouTube API or use youtube-transcript-api here
        # For this demo, we'll return a placeholder explaining what we would do
        
        return f"""
This is a placeholder for YouTube video transcript content from video ID: {video_id}

In a full implementation, TaskTamer would:
1. Use the YouTube Data API or a library like youtube-transcript-api to fetch actual captions
2. Process closed captions or auto-generated transcripts if available
3. Provide a complete transcript of the video content

The quiz would then be generated based on the actual transcript content.

For demonstration purposes, let's assume this is the transcript of an educational video about task management strategies:

Task management is essential for productivity. Breaking complex tasks into smaller steps helps make them more manageable. The Pomodoro Technique suggests working in focused intervals of 25 minutes followed by short breaks. Another effective strategy is time blocking, where you schedule specific activities during designated time slots. Prioritization is also crucial - the Eisenhower Matrix helps categorize tasks by urgency and importance. Regular reviews of your task list help ensure you're on track and making progress toward your goals. Digital tools can enhance task management by providing reminders, organization features, and synchronization across devices.
"""
    except Exception as e:
        return f"Error processing YouTube video: {str(e)}"

def generate_questions_from_text(text, num_questions=5):
    """Generate questions using simple text analysis
    This is a simplified version that creates basic questions from text
    In a real implementation, this would use an AI model"""
    
    # Reset the quiz state
    quiz_generator.reset_quiz()
    
    if not text or len(text) < 50:
        # Use sample questions if text is too short
        questions = SAMPLE_QUESTIONS[:num_questions]
        quiz_generator.questions = questions
        quiz_generator.total_questions = len(questions)
        return questions
    
    # Check if content is a URL
    if text.strip().startswith(('http://', 'https://')):
        url = text.strip()
        # Fetch content from URL
        text = fetch_webpage_content(url)
    
    # Very simple question generator (would be replaced with AI in production)
    # This just creates placeholder questions based on text words
    paragraphs = text.split('\n')
    paragraphs = [p for p in paragraphs if len(p) > 50]  # Only consider substantial paragraphs
    
    questions = []
    for i in range(min(num_questions, len(paragraphs))):
        if i < len(paragraphs):
            paragraph = paragraphs[i]
            words = paragraph.split()
            important_words = [w for w in words if len(w) > 5][:10]
            
            if important_words:
                keyword = random.choice(important_words)
                questions.append({
                    "question": f"Which concept is related to '{keyword}' in the text?",
                    "correct_answer": paragraph[:50] + "...",
                    "incorrect_answers": [
                        "This is not mentioned in the text",
                        "The text discusses a different topic",
                        "This concept is only mentioned briefly"
                    ]
                })
    
    # Add sample questions if we didn't generate enough
    if len(questions) < num_questions:
        questions.extend(SAMPLE_QUESTIONS[:num_questions-len(questions)])
    
    # Store questions in the quiz generator
    quiz_generator.questions = questions
    quiz_generator.total_questions = len(questions)
    
    return questions

def get_formatted_questions():
    """Returns the questions with randomized options"""
    formatted_questions = []
    
    for idx, question in enumerate(quiz_generator.questions):
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
    """Record user answer in the quiz generator"""
    quiz_generator.record_answer(question_idx, selected_answer)

def get_quiz_results():
    """Get quiz results and feedback"""
    score, percentage = quiz_generator.get_score()
    feedback = quiz_generator.get_feedback()
    
    return {
        'score': score,
        'total': len(quiz_generator.questions),
        'percentage': percentage,
        'feedback': feedback
    }

def get_quiz_download(format='csv'):
    """Get downloadable quiz content"""
    return quiz_generator.get_download_content(format)

# For compatibility with the existing code
def generate_questions(documents, num_questions=5):
    """Legacy interface for compatibility"""
    if isinstance(documents, str):
        return generate_questions_from_text(documents, num_questions)
    return generate_questions_from_text("", num_questions)  # Fallback to sample questions