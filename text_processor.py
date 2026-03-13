from pypdf import PdfReader
import streamlit as st


def extract_text_from_pdf(uploaded_file):
    pdf = PdfReader(uploaded_file)
    text = ""

    for page in pdf.pages:
        text += page.extract_text()

    return text


def split_text_into_chunks(text, chunk_size=1000, overlap=200):
    chunks = []

    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)

        start = end - overlap

    return chunks

def retrieve_relevant_chunks(chunks, query, top_k=3):
    relevant_chunks = []

    for chunk in chunks:
        if query.lower() in chunk.lower():
            relevant_chunks.append(chunk)

    return relevant_chunks[:top_k]

