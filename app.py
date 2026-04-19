import streamlit as st
import time
from gtts import gTTS

from text_processor import (
    extract_text_from_pdf,
    split_text_into_chunks,
    summarize_document,
    answer_question,
)
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from rag import get_relevant_chunks

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# ---------------- UI ----------------
st.markdown("""
<style>
.stApp {background: linear-gradient(135deg, #eef6ff, #c7dcff);}
.block-container {max-width: 850px;margin: auto;}
.hero {text-align:center;margin-top:40px;margin-bottom:30px;}
.hero h1 {font-size:42px;font-weight:700;color:#0f172a;}
.hero p {color:#475569;}
.stButton button {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color:white;border-radius:999px;padding:10px 20px;border:none;
}
.card {
    background: rgba(255,255,255,0.85);
    padding:20px;border-radius:16px;margin-top:15px;
}
.answer-box {
    background:#dcfce7;padding:12px;border-radius:12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HERO ----------------
st.markdown("""
<div class="hero">
<h1>☁️ AI Study Assistant</h1>
<p>Calm, focused learning</p>
</div>
""", unsafe_allow_html=True)

# ---------------- NAV ----------------
page = st.sidebar.radio("Navigate", ["Upload", "Summary", "Q&A", "Quiz", "Flashcards"])

# ---------------- SESSION ----------------
if "quiz" not in st.session_state:
    st.session_state.quiz = None
    st.session_state.index = 0
    st.session_state.score = 0
    st.session_state.answered = False

# ---------------- UPLOAD ----------------
uploaded_files = st.file_uploader("Upload PDFs", type=["pdf"], accept_multiple_files=True)

if not uploaded_files:
    st.stop()

# ---------------- PROCESS ----------------
all_text = ""
for file in uploaded_files:
    all_text += " ".join(extract_text_from_pdf(file))

chunks = split_text_into_chunks(all_text)
context = " ".join(get_relevant_chunks(chunks, "important concepts"))

# ---------------- SUMMARY (WITH TTS) ----------------
if page == "Summary":

    summary = summarize_document(all_text)

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write(summary)
    st.markdown("</div>", unsafe_allow_html=True)

    if st.button("🔊 Listen to Summary"):
        tts = gTTS(summary)
        tts.save("summary.mp3")
        st.audio("summary.mp3")

# ---------------- Q&A ----------------
if page == "Q&A":
    q = st.text_input("Ask something...")
    if st.button("Get Answer"):
        ans = answer_question(context, q)
        st.markdown(f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True)

# ---------------- QUIZ (OLD STYLE FIXED) ----------------
if page == "Quiz":

    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    num_q = st.slider("Questions", 1, 10, 3)

    if st.button("Start Quiz"):
        st.session_state.quiz = generate_quiz(context, difficulty, num_q)
        st.session_state.index = 0
        st.session_state.score = 0
        st.session_state.answered = False

    if st.session_state.quiz:

        q = st.session_state.quiz[st.session_state.index]

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        st.markdown(f"### Question {st.session_state.index+1}/{len(st.session_state.quiz)}")
        st.write(q["question"])

        selected = st.radio(
            "Choose:",
            q["options"],
            key=f"q_{st.session_state.index}"
        )

        # SUBMIT
        if st.button("Submit Answer"):
            if not st.session_state.answered:

                correct = q["options"][q["correct_index"]]

                if selected == correct:
                    st.success("✅ Correct")
                    st.session_state.score += 1
                else:
                    st.error("❌ Wrong")
                    st.info(f"Correct: {correct}")

                st.session_state.answered = True

        # NAVIGATION
        col1, col2 = st.columns(2)

        with col1:
            if st.button("⬅ Prev"):
                if st.session_state.index > 0:
                    st.session_state.index -= 1
                    st.session_state.answered = False

        with col2:
            if st.button("Next ➡"):
                if st.session_state.index < len(st.session_state.quiz) - 1:
                    st.session_state.index += 1
                    st.session_state.answered = False

        st.markdown("</div>", unsafe_allow_html=True)

        # FINAL SCORE
        if st.session_state.index == len(st.session_state.quiz) - 1:
            st.write("---")

            score = st.session_state.score
            total = len(st.session_state.quiz)

            st.success(f"🎯 Score: {score}/{total}")

            if score == total:
                st.balloons()
                st.success("🎉 Perfect Score!")

# ---------------- FLASHCARDS ----------------
if page == "Flashcards":

    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="flash")

    if "cards" not in st.session_state:
        st.session_state.cards = []
        st.session_state.card_index = 0
        st.session_state.flip = False

    if st.button("Generate Flashcards"):
        st.session_state.cards = generate_flashcards(context, difficulty, 10)
        st.session_state.card_index = 0
        st.session_state.flip = False

    if st.session_state.cards:
        card = st.session_state.cards[st.session_state.card_index]

        content = card["back"] if st.session_state.flip else card["front"]

        st.markdown(f"""
        <div class="card" style="text-align:center; font-size:18px;">
        {content}
        </div>
        """, unsafe_allow_html=True)

        if st.button("Flip"):
            st.session_state.flip = not st.session_state.flip

        col1, col2 = st.columns(2)

        if col1.button("Prev"):
            if st.session_state.card_index > 0:
                st.session_state.card_index -= 1
                st.session_state.flip = False

        if col2.button("Next"):
            if st.session_state.card_index < len(st.session_state.cards) - 1:
                st.session_state.card_index += 1
                st.session_state.flip = False