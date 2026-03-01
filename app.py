import streamlit as st
from pypdf import PdfReader
from quiz_generator import generate_quiz

st.title("📚 Educational Content Generator AI")
st.write("Welcome to your AI Study Assistant!")

uploaded_file = st.file_uploader("Upload a PDF file", type=["pdf"])

if uploaded_file is not None:
    st.success("File uploaded successfully!")

    pdf = PdfReader(uploaded_file)
    text = ""

    for page in pdf.pages:
        text += page.extract_text()

    st.subheader("Extracted Text Preview:")
    st.write(text[:1000])

    if st.button("Generate Quiz"):
        with st.spinner("Generating quiz..."):
            quiz = generate_quiz(text[:3000])  # limit text size
        st.subheader("Generated Quiz:")
        st.write(quiz) 