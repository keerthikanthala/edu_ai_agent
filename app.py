import streamlit as st
from text_processor import extract_text_from_pdf, split_text_into_chunks, summarize_document
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from text_processor import answer_question

st.set_page_config(page_title="AI Study Assistant", layout="wide")

# ---------- 🎨 PASTEL STYLE ----------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f3e7ff, #e3f2fd);
}
.stButton>button {
    background: #b39ddb;
    color: white;
    border-radius: 10px;
    border: none;
}
button[data-baseweb="tab"][aria-selected="true"] {
    color: #7e57c2;
    border-bottom: 3px solid #7e57c2;
}
h1, h2, h3 {
    color: #5e35b1;
}
</style>
""", unsafe_allow_html=True)

# ---------- TITLE ----------
st.title("📚 AI Study Assistant ✨")
st.write("Upload PDFs → Summary, Quiz, Flashcards 💜")
st.markdown("---")

# ---------- FILE UPLOAD ----------
uploaded_files = st.file_uploader(
    "Upload PDF documents",
    type=["pdf"],
    accept_multiple_files=True
)

if not uploaded_files:
    st.warning("Please upload at least one PDF file")
    st.stop()

# ---------- TEXT ----------
all_pages = []
for file in uploaded_files:
    pages = extract_text_from_pdf(file)
    all_pages.extend(pages)

if not all_pages:
    st.error("No text extracted")
    st.stop()

all_text = " ".join(all_pages)
chunks = split_text_into_chunks(all_text)

# ---------- STATS ----------
st.subheader("📊 Document Statistics")
col1, col2 = st.columns(2)

col1.metric("📄 Characters", len(all_text))
col2.metric("🧩 Chunks", len(chunks))

st.markdown("---")

context = " ".join(chunks[::max(1, len(chunks)//8)])

# ---------- TABS ----------
tab1, tab2, tab3, tab4 = st.tabs([
    "📄 Summary",
    "❓ Q&A",
    "🧠 Quiz",
    "🧾 Flashcards"
])

# ---------- SUMMARY ----------
with tab1:
    st.subheader("📄 Summary ✨")

    try:
        if "summary" not in st.session_state:
            st.session_state.summary = summarize_document(all_text)

        st.success("Summary Ready 💜")
        st.write(st.session_state.summary)

    except:
        st.error("⚠️ Summary unavailable (API limit)")

# ---------- Q&A ----------
with tab2:
    st.subheader("❓ Ask Questions 🤖")

    user_question = st.text_input("Ask anything...", key="qa_input")

    if st.button("Get Answer", key="qa_btn"):
        if user_question.strip() == "":
            st.warning("Enter a question")
        else:
            with st.spinner("Thinking..."):
                ans = answer_question(context, user_question)

            st.success("Answer Ready 💡")
            st.write(ans)

# ---------- QUIZ ----------
with tab3:
    st.subheader("🧠 Quiz 🔥")

    difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
    num_questions = st.slider("Questions", 1, 10, 3)

    if "quiz" not in st.session_state:
        st.session_state.quiz = None

    if st.button("Generate Quiz", key="quiz_btn"):
        with st.spinner("Generating..."):
            st.session_state.quiz = generate_quiz(context, difficulty, num_questions)

    if st.session_state.quiz:
        st.subheader("📝 Answer Below")

        user_answers = []

        for i, q in enumerate(st.session_state.quiz):
            st.markdown(f"**Q{i+1}: {q['question']}**")
            ans = st.radio("", q["options"], key=f"q_{i}")
            user_answers.append(ans)

        if st.button("Submit Quiz"):
            score = 0

            def normalize(text):
                return "".join(e for e in text.lower() if e.isalnum())

            for i, q in enumerate(st.session_state.quiz):
                user_ans = normalize(user_answers[i])
                correct_ans = normalize(q["answer"])

                if user_ans == correct_ans or user_ans in correct_ans or correct_ans in user_ans:
                    score += 1

            st.success(f"🎯 Score: {score}/{len(st.session_state.quiz)}")

            if score == len(st.session_state.quiz):
                st.balloons()

# ---------- FLASHCARDS (UI UPGRADED ONLY) ----------
with tab4:
    st.subheader("🧾 Flashcards 💡")

    if "cards" not in st.session_state:
        st.session_state.cards = None

    if st.button("Generate Flashcards", key="flash_btn"):
        with st.spinner("Generating..."):
            st.session_state.cards = generate_flashcards(context, difficulty, 12)

    if st.session_state.cards:
        for i, card in enumerate(st.session_state.cards):

            st.markdown(f"""
            <div style="
                background: #ffffffcc;
                padding: 20px;
                border-radius: 15px;
                margin-bottom: 15px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            ">
                <b>Q{i+1}:</b> {card['front']}
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"✨ Show Answer", key=f"card_{i}"):
                st.success(card["back"])

        st.download_button(
            "⬇️ Download Flashcards",
            data=str(st.session_state.cards),
            file_name="flashcards.txt"
        )