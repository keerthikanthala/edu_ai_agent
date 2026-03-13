from text_processor import extract_text_from_pdf,split_text_into_chunks
import streamlit as st
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards
from text_processor import retrieve_relevant_chunks

st.title("📚 Educational Content Generator AI")
st.write("Welcome to your AI Study Assistant!")

uploaded_files = st.file_uploader("Upload PDF documents", type=["pdf"],accept_multiple_files=True)

if uploaded_files is not None:
 
     all_text = ""

for file in uploaded_files:
    text = extract_text_from_pdf(file)
    all_text += text

    chunks = split_text_into_chunks(all_text)

    st.subheader("Document Statistics")
    st.write(f"Total characters in document: {len(all_text)}")
    st.write(f"Total chunks created: {len(chunks)}")

    query = "quiz questions"

    relevant_chunks = retrieve_relevant_chunks(chunks, query)

    context = " ".join(relevant_chunks)

    st.write(f"Document split into {len(chunks)} chunks.")#helps user understand document size
    st.subheader("Extracted Text Preview:")
    st.write(text[:1000])

    query = "quiz questions"

    relevant_chunks = retrieve_relevant_chunks(chunks, query)

    context = " ".join(relevant_chunks)


    difficulty = st.selectbox("Select Quiz Difficulty",["Easy","Medium","Hard"])

    if not text:
        st.error("No text could be extracted from this PDF")

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            context = " ".join(chunks[:3])
            quiz = generate_quiz(context)  # limit text size
        st.subheader("Generated Quiz:")
        st.write(quiz) 

    if st.button("Generate Flashcards"):
        with st.spinner("Generating flashcards..."):
            flashcards = generate_flashcards(chunks[0])
        st.subheader("Flashcards:")
        st.write(flashcards)

    