import streamlit as st
from text_processor import extract_text_from_pdf, split_text_into_chunks, summarize_document, answer_question
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from rag import get_relevant_chunks

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="AI Study Assistant", layout="wide")

# ---------------- PERFECT CONTRAST UI ----------------
st.markdown("""
<style>

/* Background */
.stApp {
    background: linear-gradient(135deg, #0f172a, #1e293b);
}

/* Text visibility FIX */
h1, h2, h3, h4, h5, h6, p, label, span, div {
    color: #f8fafc !important;
}

/* Subtext */
small, .stCaption {
    color: #cbd5e1 !important;
}

/* Inputs FIX */
.stTextInput input, .stSelectbox div, .stSlider {
    background: #1e293b !important;
    color: white !important;
    border-radius: 10px !important;
}

/* Radio buttons FIX */
.stRadio label {
    color: #e2e8f0 !important;
    font-size: 16px;
}

/* Buttons */
.stButton button {
    background: linear-gradient(135deg, #3b82f6, #06b6d4);
    color: white;
    border-radius: 12px;
    border: none;
    padding: 10px 20px;
    font-weight: 500;
}

/* File uploader FIX */
[data-testid="stFileUploader"] button {
    background: rgba(255,255,255,0.2) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.4) !important;
}

/* Cards */
.glass {
    background: rgba(255,255,255,0.08);
    padding: 25px;
    border-radius: 16px;
    border: 1px solid rgba(255,255,255,0.2);
}

/* Answer box */
.answer-box {
    background: #14532d;
    padding: 15px;
    border-radius: 12px;
    color: white;
    margin-top: 10px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("<h1 style='text-align:center;'>📚 AI Study Assistant</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Learn faster. Study smarter.</p>", unsafe_allow_html=True)

# ---------------- FEATURES ----------------
col1, col2, col3 = st.columns(3)

col1.markdown('<div class="glass"><h4>🧠 Quiz</h4></div>', unsafe_allow_html=True)
col2.markdown('<div class="glass"><h4>📄 Summary</h4></div>', unsafe_allow_html=True)
col3.markdown('<div class="glass"><h4>🧾 Flashcards</h4></div>', unsafe_allow_html=True)

# ---------------- FILE UPLOAD ----------------
uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if not uploaded_files:
    st.warning("Upload a PDF to continue")
    st.stop()

# ---------------- PROCESS ----------------
all_text = ""
for file in uploaded_files:
    all_text += " ".join(extract_text_from_pdf(file))

chunks = split_text_into_chunks(all_text)

# ---------------- SUMMARY ----------------
st.subheader("📄 Summary")

if "summary" not in st.session_state:
    st.session_state.summary = summarize_document(all_text)

st.markdown(f'<div class="glass">{st.session_state.summary}</div>', unsafe_allow_html=True)

# ---------------- CONTEXT ----------------
topic = st.text_input("Enter topic (optional)")
query = topic if topic else "important concepts"
context = " ".join(get_relevant_chunks(chunks, query))

# ---------------- Q&A ----------------
st.subheader("❓ Ask Question")

q = st.text_input("Type your question")

if st.button("Get Answer"):
    ans = answer_question(context, q)
    st.markdown(f'<div class="answer-box">{ans}</div>', unsafe_allow_html=True)

# ---------------- QUIZ ----------------
st.subheader("🧠 Quiz")

difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
num_q = st.slider("Questions", 1, 10, 3)

if "quiz" not in st.session_state:
    st.session_state.quiz = None

if st.button("Generate Quiz"):
    st.session_state.quiz = generate_quiz(context, difficulty, num_q)

if st.session_state.quiz:
    answers = []

    for i, q in enumerate(st.session_state.quiz):
        st.markdown(f"### Q{i+1}. {q['question']}")
        ans = st.radio("Select:", q["options"], key=f"q_{i}")
        answers.append(ans)

    if st.button("Submit Quiz"):

        score = 0
        total = len(st.session_state.quiz)

        for i, q in enumerate(st.session_state.quiz):
            correct = q["options"][ord(q["answer"]) - 65]
            if answers[i] == correct:
                score += 1

        # 🎉 CONFETTI FIX
        if score == total:
            st.balloons()

        st.success(f"🎯 Score: {score}/{total}")

# ---------------- FLASHCARDS ----------------
st.subheader("🧾 Flashcards")

if "cards" not in st.session_state:
    st.session_state.cards = []
    st.session_state.index = 0

if st.button("Generate Flashcards"):
    st.session_state.cards = generate_flashcards(context, difficulty, 10)
    st.session_state.index = 0

if st.session_state.cards:
    card = st.session_state.cards[st.session_state.index]

    st.markdown(f"### Card {st.session_state.index+1}/{len(st.session_state.cards)}")

    st.markdown(f'<div class="glass">{card["front"]}</div>', unsafe_allow_html=True)

    if st.button("Show Answer"):
        st.markdown(f'<div class="answer-box">{card["back"]}</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    if col1.button("Next"):
        if st.session_state.index < len(st.session_state.cards) - 1:
            st.session_state.index += 1

    if col2.button("Restart"):
        st.session_state.index = 0