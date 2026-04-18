import streamlit as st
import time
from text_processor import extract_text_from_pdf, split_text_into_chunks, summarize_document, answer_question
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from rag import get_relevant_chunks
from database import init_db, log_progress, log_flashcard_review, get_progress
from gtts import gTTS

init_db()

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
            
    # Using the same chunks variable you already defined
    qa_chunks = get_relevanwer-box {
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

# ---------------- AUDIO SUMMARY ----------------
st.subheader("🔊 Listen to Summary")

if st.button("Play Summary Audio"):
    summary_text = st.session_state.summary
    tts = gTTS(summary_text)
    tts.save("summary.mp3")
    st.audio("summary.mp3")

# ---------------- CONTEXT ----------------
topic = st.text_input("Enter topic (optional)")
query = topic if topic else "important concepts"
context = " ".join(get_relevant_chunks(chunks, query))

# ---------------- Q&A ----------------
st.subheader("❓ Ask Question")

q = st.text_input("Type your question")

if st.button("Get Answer"):
    try:
        qa_chunks = get_relevant_chunks(chunks, q)
        qa_context = " ".join(qa_chunks)
        ans = answer_question(qa_context, q)

        # Save answer in session state so it persists
        st.session_state.last_answer = ans

        st.markdown(f'<div class="answer-box">{ans}</div>', unsafe_allow_html=True)

        st.subheader("📄 Source")
        for chunk in qa_chunks:
            st.markdown(f"<div class='glass'>{chunk[:200]}...</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"⚠️ Could not generate answer: {e}")

# ---- Text-to-Speech for Q&A Answer ----
if "last_answer" in st.session_state and st.session_state.last_answer:
    if st.button("Play Answer Audio"):
        tts = gTTS(st.session_state.last_answer)
        tts.save("answer.mp3")
        st.audio("answer.mp3")

# ---------------- QUIZ ----------------
st.subheader("🧠 Quiz")
difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
num_q = st.slider("Questions", 1, 10, 3)

if "quiz" not in st.session_state:
    st.session_state.quiz = None
    st.session_state.answers = {}
    st.session_state.quiz_start = None
    st.session_state.quiz_duration = None
    st.session_state.quiz_result = None

# Generate quiz with timer
if st.button("Generate Timed Quiz"):
    quiz_chunks = get_relevant_chunks(chunks, query)
    quiz_context = " ".join(quiz_chunks)
    st.session_state.quiz = generate_quiz(quiz_context, difficulty, num_q)
    st.session_state.quiz_start = time.time()
    st.session_state.quiz_duration = num_q * 30  # 30 seconds per question
    st.session_state.answers = {}
    st.session_state.quiz_result = None

# Show quiz if generated
if st.session_state.quiz and not st.session_state.quiz_result:
    elapsed = int(time.time() - st.session_state.quiz_start)
    remaining = st.session_state.quiz_duration - elapsed
    if remaining > 0:
        st.warning(f"⏱️ Time left: {remaining} seconds")
    else:
        st.error("Time is up! Auto‑submitting your answers...")
        submitted = True
    submitted = False

    with st.form(key="quiz_form"):
        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"### Q{i+1}. {q['question']}")
            labels = [f"{j+1}. {opt}" for j, opt in enumerate(q["options"])]
            choice = st.radio("", labels, key=f"q_{i}")
            st.session_state.answers[f"q_{i}"] = int(choice.split(".")[0]) - 1
        submitted = st.form_submit_button("Submit Quiz") or submitted

        if submitted and not st.session_state.quiz_result:
            score = 0
            total = len(st.session_state.quiz)
            wrong_items = []
            for i, q in enumerate(st.session_state.quiz):
                selected = st.session_state.answers.get(f"q_{i}", None)
                if selected == q.get("correct_index"):
                    score += 1
                else:
                    wrong_items.append((q, selected))

            st.session_state.quiz_result = {
                "score": score,
                "total": total,
                "wrong_items": wrong_items,
            }
            log_progress("quiz", score, total, difficulty=difficulty, topic=query)

# ---------------- RESULTS + EXPLANATIONS ----------------
if st.session_state.get("quiz_result"):
    result = st.session_state.quiz_result
    st.success(f"🎯 Score: {result['score']}/{result['total']}")

    if result["wrong_items"]:
        st.subheader("Review")
        for q, sel in result["wrong_items"]:
            st.markdown(f"**Q:** {q['question']}")
            st.markdown(f"**Your answer:** {q['options'][sel] if sel is not None else 'No answer'}")
            st.markdown(f"**Correct answer:** {q['options'][q['correct_index']]}")
            if q.get("explanation"):
                st.markdown(f"**Explanation:** {q['explanation']}")
            st.markdown("---")

        # Recommended flashcards
        st.subheader("🔁 Recommended Flashcards")
        wrong_text = " ".join([q["question"] for q, _ in result["wrong_items"]])
        recommended_cards = generate_flashcards(wrong_text, difficulty, 5)
        for idx, card in enumerate(recommended_cards):
            st.markdown(f"**Q:** {card['front']}")
            if st.button("Show Answer", key=f"rec_{idx}"):
                st.markdown(f"**A:** {card['back']}")
    else:
        st.info("✅ You got everything correct! No recommended flashcards needed.")

# ---------------- OVERALL FLASHCARDS ----------------
st.subheader("📚 Overall Flashcards")
if "cards" not in st.session_state:
    st.session_state.cards = []
    st.session_state.card_index = 0
    st.session_state.show_answer = False

if st.button("Generate Overall Flashcards"):
    st.session_state.cards = generate_flashcards(context, difficulty, 10)
    st.session_state.card_index = 0
    st.session_state.show_answer = False

if st.session_state.cards:
    card = st.session_state.cards[st.session_state.card_index]
    st.markdown(f"### Card {st.session_state.card_index+1}/{len(st.session_state.cards)}")
    st.markdown(f'<div class="glass">{card["front"]}</div>', unsafe_allow_html=True)

    if st.button("Show Answer"):
        st.session_state.show_answer = True
        log_flashcard_review(card["front"], card["back"], correct=False)

    if st.session_state.show_answer:
        st.markdown(f'<div class="answer-box">{card["back"]}</div>', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        if col1.button("I knew this", key="knew"):
            log_flashcard_review(card["front"], card["back"], correct=True)
            st.session_state.show_answer = False
            if st.session_state.card_index < len(st.session_state.cards) - 1:
                st.session_state.card_index += 1
        if col2.button("I didn't know", key="didnt"):
            log_flashcard_review(card["front"], card["back"], correct=False)
            st.session_state.show_answer = False
            if st.session_state.card_index < len(st.session_state.cards) - 1:
                st.session_state.card_index += 1
        if col3.button("Restart", key="restart"):
            st.session_state.card_index = 0
            st.session_state.show_answer = False
    else:
        coln, coln2 = st.columns(2)
        if coln.button("Next", key="next_no_show"):
            if st.session_state.card_index < len(st.session_state.cards) - 1:
                st.session_state.card_index += 1
        if coln2.button("Restart", key="restart_no_show"):
            st.session_state.card_index = 0
            st.session_state.show_answer = False            

# ---------------- PERFORMANCE ANALYTICS ----------------
from database import get_progress, clear_progress

st.subheader("📊 Performance Analytics")

# Add reset button
if st.button("Reset Performance Analytics"):
    clear_progress()
    st.success("Performance data cleared!")

progress = get_progress()
if progress:
    for feature, score, total, difficulty_meta, topic_meta, timestamp in progress:
        if total > 0:
            percent = round((score / total) * 100, 1)
            st.write(f"{feature} ({difficulty_meta or 'N/A'}) - {score}/{total} ({percent}%) — {topic_meta or ''} — {timestamp}")

            if percent < 50:
                st.warning("Needs improvement — review flashcards daily.")
            elif percent < 80:
                st.info("Good progress — keep practicing quizzes regularly.")
            else:
                st.success("Excellent — you’re ready for harder topics!")
else:
    st.info("No performance data yet. Try a quiz or flashcards to see progress here.")
