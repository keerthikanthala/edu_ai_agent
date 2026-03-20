from text_processor import extract_text_from_pdf, split_text_into_chunks, summarize_document
import streamlit as st
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards

st.title("Educational Content Generator AI")
st.write("Welcome to your AI Study Assistant")

uploaded_files = st.file_uploader(
    "Upload PDF documents",
    type=["pdf"],
    accept_multiple_files=True
)

if uploaded_files:

    all_pages = []

    # Extract text from PDFs
    for file in uploaded_files:
        pages = extract_text_from_pdf(file)
        all_pages.extend(pages)

    if not all_pages:
        st.error("No text could be extracted from the uploaded PDFs")

    else:

        all_text = " ".join(all_pages)

        chunks = split_text_into_chunks(all_text)

        st.subheader("Document Statistics")
        st.write(f"Total characters: {len(all_text)}")
        st.write(f"Total chunks created: {len(chunks)}")

        # -------- SUMMARY (FOR USER ONLY) --------

        st.subheader("Document Summary")

        summary = summarize_document(all_text)

        st.write(summary)

        # -----------------------------------------

        # Select chunks from across the document
        step = max(1, len(chunks)//5)

        selected_chunks = []

        for i in range(0, len(chunks), step):
            selected_chunks.append(chunks[i])

        context = " ".join(selected_chunks[:5])

     # INPUT BOX TO ASK ANYTHING OTHER THAN QUIZ OR FLASHCARDS
        question = st.text_input("Ask a question from the document")

    if question:
      relevant_chunks = retrieve_relevant_chunks(chunks, question)
      context = " ".join(relevant_chunks)

      answer = generate_quiz(context)

      st.subheader("Answer:")
      st.write(answer)

        # -------- QUIZ SETTINGS --------

    difficulty = st.selectbox(
            "Select Quiz Difficulty",
            ["Easy", "Medium", "Hard"],
            key="quiz_difficulty"
        )

    num_questions = st.slider(
            "Number of Questions",
            1,
            10,
            3
        )

        # -------- QUIZ --------

    if st.button("Generate Quiz"):

            with st.spinner("Generating quiz..."):

                quiz = generate_quiz(
                    context,
                    difficulty,
                    num_questions
                )

            st.subheader("Generated Quiz")
            st.write(quiz)

        # -------- FLASHCARDS --------

    if st.button("Generate Flashcards"):

            # Decide flashcard count automatically
            if len(chunks) <= 5:
                num_flashcards = 5
            elif len(chunks) <= 10:
                num_flashcards = 8
            else:
                num_flashcards = 12

            with st.spinner("Generating flashcards..."):

                flashcards = generate_flashcards(
                    context,
                    difficulty,
                    num_flashcards
                )

            st.subheader("Flashcards")
            st.write(flashcards)