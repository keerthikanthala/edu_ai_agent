from text_processor import extract_text_from_pdf,split_text_into_chunks
import streamlit as st
from quiz_generator import generate_quiz
from flashcard_generator import generate_flashcards

st.title("📚 Educational Content Generator AI")
st.write("Welcome to your AI Study Assistant!")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:

    text = extract_text_from_pdf(uploaded_file)

    chunks = split_text_into_chunks(text)

    st.write(f"Document split into {len(chunks)} chunks.")

    st.subheader("Extracted Text Preview:")
    st.write(text[:1000])

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            context = " ".join(chunks[:2])
            quiz = generate_quiz(context)  # limit text size
        st.subheader("Generated Quiz:")
        st.write(quiz) 

    if st.button("Generate Flashcards"):
        with st.spinner("Generating flashcards..."):
            flashcards = generate_flashcards(chunks[0])
        st.subheader("Flashcards:")
        st.write(flashcards)