import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"),
)

def generate_quiz(text):
    text = text[:3000]  # limit text size

    prompt = f"""
    Generate 3 multiple choice questions from the following educational content.

    For each question provide:
    Question:
    A)
    B)
    C)
    D)
    Correct Answer:

    Content:
    {text}
    """

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=0.5,
    )

    return completion.choices[0].message.content