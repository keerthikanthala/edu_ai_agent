from pypdf import PdfReader
from groq import Groq
from dotenv import load_dotenv
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
from pypdf import PdfReader


def extract_text_from_pdf(uploaded_file):

    pdf = PdfReader(uploaded_file)

    pages_text = []

    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            pages_text.append(page_text)

    return pages_text


def split_text_into_chunks(text, chunk_size=1000, overlap=200):

    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        chunks.append(chunk)

        start = end - overlap

    return chunks


def retrieve_relevant_chunks(chunks, query=None, top_k=5):

    if query:
        relevant_chunks = []

        for chunk in chunks:
            if query.lower() in chunk.lower():
                relevant_chunks.append(chunk)

        if relevant_chunks:
            return relevant_chunks[:top_k]

    # fallback: spread chunks across the document
    step = max(1, len(chunks) // top_k)

    selected_chunks = []
    for i in range(0, len(chunks), step):
        selected_chunks.append(chunks[i])

    return selected_chunks[:top_k]


from groq import Groq
import os

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def summarize_document(text):

    text = text[:5000]

    prompt = f"""
Summarize the following educational document.
Provide a clear summary covering the key ideas.

Document:
{text}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return completion.choices[0].message.content