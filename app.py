from gtts import gTTS
import streamlit as st
import time
import time

from text_processor import extract_text_from_pdf, split_text_into_chunks, summarize_document, answer_question
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from rag import get_relevant_chunks
from database import init_db, log_progress, log_flashcard_review, get_progress
from gtts import gTTS

init_db()

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# ---------------- PREMIUM UI ----------------
st.markdown("""
<style>

.stApp {
    background: linear-gradient(135deg, #eef6ff, #c7dcff);
}

.block-container {
    max-width: 850px;
    margin: auto;
}

/* HERO */
.hero {
    text-align:center;
    margin-top:40px;
    margin-bottom:30px;
}

.hero h1 {
    font-size:42px;
    font-weight:700;
    color:#0f172a;
}

.hero p {
    color:#475569;
}

/* BUTTON */
.stButton button {
    background: linear-gradient(90deg, #2563eb, #3b82f6);
    color:white;
    border-radius:999px;
    padding:10px 20px;
    border:none;
}

/* CARD */
.card {
    background: rgba(255,255,255,0.8);
    backdrop-filter: blur(10px);
    padding:20px;
    border-radius:16px;
    margin-top:15px;
}

/* ANSWER */
            
    # Using the same chunks variable you already defined
    qa_chunks = get_relevanwer-box {
    background:#dcfce7;
    padding:12px;
    border-radius:12px;
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

# ---------------- SUMMARY ----------------
if page == "Summary":

    summary = summarize_document(all_text)  # ✅ STORE IT

    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.write(summary)
    st.markdown("</div>", unsafe_allow_html=True)

# ---------------- AUDIO SUMMARY ----------------
st.subheader("🔊 Listen to Summary")

if st.button("Play Summary Audio"):
    summary_text = st.session_state.summary
    tts = gTTS(summary_text)
    tts.save("summary.mp3")
    st.audio("summary.mp3")

    # 🔊 TEXT TO SPEECH BUTTON
    if st.button("🔊 Listen to Summary"):
        from gtts import gTTS

        tts = gTTS(summary)
        tts.save("summary.mp3")

        st.audio("summary.mp3")

# ---------------- Q&A ----------------
if page == "Q&A":
    q = st.text_input("Ask something...")
    if st.button("Get Answer"):
    try:
        qa_chunks = get_relevant_chunks(chunks, q)
        qa_context = " ".join(qa_chunks)
            ans = answer_question(qa_context, q)

        # Save answer in session state so it persists
        st.session_state.last_answer = ans

            st.markdown(f"<div class='answer-box'>{ans}</div>", unsafe_allow_html=True)

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
if page == "Quiz":
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
    if "quiz" not in st.session_state:
        st.session_state.quiz = None
        st.session_state.index = 0
        st.session_state.answers = []
        st.session_state.finished = False
        st.session_state.start = None

    if st.button("Start Quiz"):
        st.session_state.quiz = generate_quiz(context, difficulty, num_q)
        st.session_state.index = 0
        st.session_state.answers = []
        st.session_state.finished = False
        st.session_state.start = time.time()

    if st.session_state.quiz and not st.session_state.finished:

        q = st.session_state.quiz[st.session_state.index]

        st.markdown("<div class='card'>", unsafe_allow_html=True)

        elapsed = int(time.time() - st.session_state.start)
        st.write(f"⏱ Time: {elapsed}s")

        st.progress((st.session_state.index+1)/len(st.session_state.quiz))

        st.markdown(f"### Question {st.session_state.index+1}/{len(st.session_state.quiz)}")
        st.write(q["question"])

        # FIX: ensure options show real values
        options = q["options"]

        selected = st.radio("Choose:", options, key=f"q_{st.session_state.index}")

        if st.button("Next ➡️"):
            st.session_state.answers.append(selected)

            if st.session_state.index < len(st.session_state.quiz)-1:
                st.session_state.index += 1
            else:
                st.session_state.finished = True

        st.markdown("</div>", unsafe_allow_html=True)

    if st.session_state.finished:

        score = 0
        total = len(st.session_state.quiz)

        st.markdown("## 📊 Analysis")

        for i, q in enumerate(st.session_state.quiz):

            # FIX: support both formats
            if len(q["answer"]) == 1 and q["answer"].isalpha():
                correct = q["options"][ord(q["answer"]) - 65]
            else:
                correct = q["answer"]

            user = st.session_state.answers[i]

            if user == correct:
                score += 1
                st.success(f"Q{i+1} ✔ Correct")
            else:
                st.error(f"Q{i+1} ❌ Your: {user} | Correct: {correct}")

        st.progress(score/total)

        if score == total:
            st.balloons()

        st.success(f"Score: {score}/{total}")

# ---------------- OVERALL FLASHCARDS ----------------
st.subheader("📚 Overall Flashcards")
if "cards" not in st.session_state:
    st.session_state.cards = []
    st.session_state.card_index = 0
    st.session_state.show_answer = False
# ---------------- FLASHCARDS ----------------
if page == "Flashcards":

    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], key="flash_diff")

    if "cards" not in st.session_state:
        st.session_state.cards = []
        st.session_state.index = 0
        st.session_state.flip = False

if st.button("Generate Overall Flashcards"):
    st.session_state.cards = generate_flashcards(context, difficulty, 10)
    st.session_state.card_index = 0
    st.session_state.show_answer = False
    if st.button("Generate Flashcards"):
        st.session_state.cards = generate_flashcards(context, difficulty, 10)
        st.session_state.index = 0
        st.session_state.flip = False

if st.session_state.cards:
    card = st.session_state.cards[st.session_state.card_index]
    st.markdown(f"### Card {st.session_state.card_index+1}/{len(st.session_state.cards)}")
    st.markdown(f'<div class="glass">{card["front"]}</div>', unsafe_allow_html=True)
    if st.session_state.cards:
        card = st.session_state.cards[st.session_state.index]

        content = card["back"] if st.session_state.flip else card["front"]

        st.markdown(f"""
        <div class="card" style="text-align:center; font-size:18px;">
        {content}
        </div>
        """, unsafe_allow_html=True)

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

        if st.button("Flip"):
            st.session_state.flip = not st.session_state.flip

        col1, col2 = st.columns(2)

        if col1.button("Prev"):
            if st.session_state.index > 0:
                st.session_state.index -= 1
                st.session_state.flip = False

        if col2.button("Next"):
            if st.session_state.index < len(st.session_state.cards)-1:
                st.session_state.index += 1
                st.session_state.flip = False