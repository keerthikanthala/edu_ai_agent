import os
import random
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def generate_flashcards(text, difficulty="Medium", num_flashcards=10):

    # If context came as chunks
    if isinstance(text, list):
        text = " ".join([str(t) for t in text])

    # ---- Sample text from different parts of document ----
    sections = []

    if len(text) > 6000:
        step = len(text) // 4

        sections.append(text[0:1500])                 # beginning
        sections.append(text[step:step+1500])         # early middle
        sections.append(text[step*2:step*2+1500])     # late middle
        sections.append(text[-1500:])                 # end

        text = " ".join(sections)
    else:
        text = text[:4000]
    # -----------------------------------------------------

    difficulty_rules = {
        "Easy": "Generate definition-based flashcards.",
        "Medium": "Generate conceptual understanding flashcards.",
        "Hard": "Generate reasoning or application-based flashcards."
    }

    difficulty_instruction = difficulty_rules.get(difficulty, "")

    prompt = f"""
You are an AI study assistant.

Create {num_flashcards} flashcards from the study material.

Difficulty: {difficulty}
Instruction: {difficulty_instruction}

Rules:
- Cover concepts from different parts of the document.
- Avoid repeating the same topic.
- Keep answers short and clear.

Format exactly like this:

Flashcard 1
Front: question
Back: answer

Flashcard 2
Front: question
Back: answer

Front and Back must always be on separate lines.

Study Material:
{text}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    result = completion.choices[0].message.content

    # Force formatting if the model compresses lines
    result = result.replace(" Flashcard", "\nFlashcard")
    result = result.replace(" Question:", "\nFront:")
    result = result.replace(" Answer:", "\nBack:")

    return result