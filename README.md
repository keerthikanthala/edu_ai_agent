Educational Content Generator AI

📌 Project Overview

Educational Content Generator AI is an AI-powered study assistant that helps students generate learning materials from PDF documents. Users can upload educational PDFs, and the system extracts the content and generates quizzes and flashcards automatically using AI.

This tool helps students quickly revise topics by converting study material into interactive learning content.

---

🚀 Features

- Upload PDF study materials
- Extract text from PDF documents
- Split text into smaller chunks for efficient processing
- Preview extracted text
- Generate AI-based quizzes
- Generate AI-based flashcards
- Simple and interactive user interface using Streamlit

---

🧠 How It Works

1. User uploads a PDF file.
2. The system extracts text from the PDF.
3. The text is divided into smaller chunks for processing.
4. AI generates quizzes and flashcards based on the document content.
5. The generated learning materials are displayed to the user.

---

🛠️ Technologies Used

- Python
- Streamlit
- Groq API
- PyPDF
- Python Dotenv

---

📂 Project Structure

edu_ai_agent/
│
├── app.py                  # Main Streamlit application
├── text_processor.py       # PDF text extraction and chunking
├── quiz_generator.py       # AI quiz generation
├── flashcard_generator.py  # AI flashcard generation
├── database.py             # Database utilities (if used)
├── utils.py                # Helper functions
├── requirements.txt        # Project dependencies
├── README.md               # Project documentation
├── .gitignore              # Files ignored by Git
└── .env                    # API keys (not uploaded to GitHub)

---

⚙️ Installation and Setup

1. Clone the Repository

git clone <repository-link>
cd edu_ai_agent

2. Create Virtual Environment

python -m venv venv

3. Activate Virtual Environment

Windows:

venv\Scripts\activate

Mac/Linux:

source venv/bin/activate

4. Install Dependencies

pip install -r requirements.txt

5. Add Environment Variables

Create a ".env" file and add your Groq API key:

GROQ_API_KEY=your_api_key_here

6. Run the Application

streamlit run app.py

---

👥 Team Members

- Member 1 – Quiz Generation
- Member 2 – Document Processing and Text Chunking
- Member 3 – UI and Integration

---

📅 Project Week

Week 2 – Document Processing and AI Content Generation

---

📚 Future Improvements

- Support multiple document uploads
- Add difficulty levels for quizzes
- Download generated quizzes and flashcards
- Improve document retrieval using advanced RAG techniques

---

Week 3 Progress (AI Logic Improvements)

Objective

Improve quiz and flashcard generation by enhancing document processing and AI prompt logic.
Work Completed

1. Document Summary Preview
Added an AI-generated summary of the uploaded PDF to give users a quick overview of the document.

2. Improved Document Processing
Implemented text chunking to handle large PDFs and ensure the system uses content from different parts of the document instead of only the first page.

3. Enhanced Quiz Generation
Improved prompt engineering to support:

selectable difficulty level

customizable number of questions

progressive difficulty (Easy → Medium → Hard)

structured MCQs with answer explanations

4. Flashcard Generation Improvements
Implemented AI-generated flashcards based on key concepts from the document with structured Front/Back formatting.

--- 

Week 4 Progress

1. Integrated all modules into app.py (text processing, quiz, flashcards)
   Implemented complete workflow: Upload → Summary → Q&A → Quiz → Flashcards
   Converted quiz to interactive format (options, scoring, explanations)
2. Added 🎉 confetti animation for correct answers
3. Improved flashcards with chunk-based generation and “Show Answer” feature
   Added document-based Q&A for user queries
4. Fixed API issues (rate limit handling, optimized input size)
5. Improved content coverage (questions from multiple parts of document)
   Enhanced UI using tabs (Summary, Q&A, Quiz, Flashcards)

---

 Week 5 Progress
 1.Designed Apple-style UI using Streamlit + custom CSS
2.Implemented glassmorphism (blur cards, gradients)
3.Fixed text contrast and visibility issues
4.Styled buttons, file uploader, inputs, and radio options
5.Removed duplicate UI and fixed layout spacing
6.Improved overall user experience and consistency
7.Managed UI flow using Streamlit session state
8.Added confetti animation for full score

---

📚 Week 6 Summary 
🛠️ Technical Fixes
- Resolved multiple Streamlit errors:
- Button conflicts inside forms.
- Deprecated API (experimental_rerun → rerun).
- Session state handling for quiz answers and flashcards.
- Cleaned up duplicate flashcard generation buttons for clarity.
🧠 Quiz System
- Built a timed quiz feature:
- Timer scales with number of questions (30s per question).
- Auto‑submission when time runs out.
- Restored explanations after answers for deeper learning.
- Added recommended flashcards tied to wrong answers.
- Structured quiz flow: generate → countdown → submit → review → targeted practice.
📝 Flashcards
- Organized into two clear modes:
- Overall Flashcards for general study.
- Recommended Flashcards for weak areas after quizzes.
- Added navigation (Next, Restart) and review logging (I knew this / I didn’t know).
- Ensured flashcards integrate smoothly with quiz results.
📊 Performance & Analytics
- Designed a Performance Analytics block:
- Tracks quiz scores, percentages, difficulty, topics, and timestamps.
- Provides motivational feedback (needs improvement / good progress / excellent).
- Discussed adding visual charts (line graphs, trends) for future enhancement.
🔹 RAG Pipeline Upgrade
- Integrated SentenceTransformer embeddings for semantic search.
- Added FAISS index for efficient retrieval.
- Implemented CrossEncoder re-ranking to ensure the most relevant chunks are used for answers.
- Optimized with caching so the app runs faster and avoids rebuilding the index each query.
🔹 Study Tracking & Analytics
- Added a SQLite database to log quiz scores each run.
- Built a performance analytics section that shows:
- Score and percentage for each quiz attempt.
- Motivational feedback messages (e.g., “Needs improvement”, “Good progress”, “Excellent”).