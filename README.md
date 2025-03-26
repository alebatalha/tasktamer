# TaskTamer

✨ **TaskTamer** is your magical productivity assistant that helps you break down complex tasks, summarize documents, and test your knowledge with quizzes.

## Features

### 📋 Task Breaker
Break down complex tasks into manageable steps with our AI-powered task decomposition tool. Mark steps as complete and save your task breakdown for later reference.

### 📝 Summarizer
Generate concise summaries from text, documents, or web content. Easily extract the key points from any content to save time and improve comprehension.

### 🧠 Quiz Master
Create knowledge quizzes based on your study materials. Test your understanding with automatically generated multiple-choice questions and track your progress.

### 🤖 TaskTamer Assistant
Get help at any time with our chat assistant that can answer questions about TaskTamer features and guide you through the application.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/tasktamer.git
   cd tasktamer
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the Streamlit app:
   ```bash
   streamlit run streamlit_app.py
   ```

## Requirements

- Python 3.8+
- Streamlit
- Farm-Haystack (optional for advanced features)
- BeautifulSoup4
- Requests

## Project Structure

```
tasktamer/
├── streamlit_app.py           # Main Streamlit application interface
├── README.md                  # Project documentation
├── requirements.txt           # Project dependencies
├── backend/
│   ├── __init__.py            # Package initializer
│   └── core.py                # Core TaskTamer functionality
```

## Usage

1. **Task Breaker**:
   - Enter a complex task in the text field
   - Click "Break Down Task" to generate actionable steps
   - Mark steps as complete and save your breakdown

2. **Summarizer**:
   - Choose your input method (text, file, or web URL)
   - Input your content
   - Click "Generate Summary" to create a concise summary
   - Save your summary for later reference

3. **Quiz Master**:
   - Choose your input method (text, file, or web URL)
   - Input your study material
   - Click "Generate Quiz" to create multiple-choice questions
   - Take the quiz and review your results

## Fallback Functionality

The app includes fallback functionality when Haystack or other advanced features are not available, ensuring it works even with limited dependencies.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit
- Uses Farm-Haystack for advanced NLP features
- Inspired by productivity tools like Goblin Tools