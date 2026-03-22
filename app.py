import streamlit as st
from text_processor import extract_text_from_pdf, split_text_into_chunks, summarize_document
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from text_processor import answer_question

st.set_page_config(page_title="AI Study Assistant", layout="wide")

st.title("📚 Educational Content Generator AI")
st.write("Welcome to your AI Study Assistant")

# ---------------- FILE UPLOAD ----------------

uploaded_files = st.file_uploader(
    "Upload PDF documents",
    type=["pdf"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.warning("Please upload at least one PDF file")
    st.stop()

# ---------------- TEXT EXTRACTION ----------------

all_pages = []

for file in uploaded_files:
    pages = extract_text_from_pdf(file)
    all_pages.extend(pages)

if not all_pages:
    st.error("No text could be extracted from the uploaded PDFs")
    st.stop()

all_text = " ".join(all_pages)
chunks = split_text_into_chunks(all_text)

# ---------------- DOCUMENT INFO ----------------

st.subheader("📊 Document Statistics")
st.write(f"Total characters: {len(all_text)}")
st.write(f"Total chunks created: {len(chunks)}")

# ---------------- SUMMARY ----------------

st.subheader("📄 Document Summary")

if "summary" not in st.session_state:
    st.session_state.summary = summarize_document(all_text)

summary = st.session_state.summary
st.write(summary)


# ---------------- CONTEXT CREATION ----------------

context = " ".join(chunks[::max(1, len(chunks)//8)])

# ---------------- Q&A SECTION ----------------

st.subheader("❓ Ask Questions from Document")

user_question = st.text_input("Type your question", key="qa_input")

if st.button("Get Answer", key="qa_button"):

    if user_question.strip() == "":
        st.warning("Please enter a question")
    else:
        with st.spinner("Thinking..."):
            answer = answer_question(context, user_question)

        st.subheader("📌 Answer")
        st.write(answer)

# ---------------- QUIZ SETTINGS ----------------

st.subheader("🧠 Quiz Settings")

difficulty = st.selectbox(
    "Select Quiz Difficulty",
    ["Easy", "Medium", "Hard"]
)

num_questions = st.slider(
    "Number of Questions",
    1,
    10,
    3
)

# ---------------- QUIZ SECTION ----------------

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if st.button("Generate Quiz"):
    with st.spinner("Generating quiz..."):
        st.session_state.quiz = generate_quiz(
            context,
            difficulty,
            num_questions
        )

if st.session_state.quiz:
    st.subheader("📝 Take the Quiz")

    user_answers = []

    for i, q in enumerate(st.session_state.quiz):
        ans = st.radio(
            q["question"],
            q["options"],
            key=f"q_{i}"
        )
        user_answers.append(ans)

    if st.button("Submit Quiz"):
        score = 0

        for i, q in enumerate(st.session_state.quiz):
            if user_answers[i] == q["answer"]:
                score += 1

        st.success(f"🎯 Score: {score}/{len(st.session_state.quiz)}")

        st.subheader("📘 Explanations")

        for q in st.session_state.quiz:
            st.write(f"✅ Correct Answer: {q['answer']}")
            st.write(f"💡 {q['explanation']}")
            st.write("---")

# ---------------- FLASHCARDS SECTION ----------------

if "cards" not in st.session_state:
    st.session_state.cards = None

if st.button("Generate Flashcards"):
    with st.spinner("Generating flashcards..."):
        st.session_state.cards = generate_flashcards(
            context,
            difficulty,
            12
        )

if st.session_state.cards:
    st.subheader("🧾 Flashcards")

    for i, card in enumerate(st.session_state.cards):
        st.write(f"**Q:** {card['front']}")

        if st.button(f"Show Answer {i}"):
            st.write(f"**A:** {card['back']}")
            st.write("---")