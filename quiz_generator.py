import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def generate_quiz(text, difficulty="Medium", num_questions=3):

    text = text[:3000]

    prompt = f"""
You are an AI quiz generator.

Generate {num_questions} multiple choice questions from the study material.

Difficulty: {difficulty}

STRICT RULES:
- Each question must have 4 options.
- Each option must be on its own line.
- Label options exactly A) B) C) D)
- Do NOT show the answer under the question.
- At the very end provide an answer key.

Study Material:
{text}

Output format:

Question 1:
A)
B)
C)
D)

Question 2:
A)
B)
C)
D)

Question 3:
A)
B)
C)
D)

Answers:
1. A
2. B
3. C
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    result = completion.choices[0].message.content

   # Force each option onto a new line if the model compresses them
    result = result.replace(" A)", "\nA)")
    result = result.replace(" B)", "\nB)")
    result = result.replace(" C)", "\nC)")
    result = result.replace(" D)", "\nD)")
    result = result.replace("A)", "\nA)")
    result = result.replace("B)", "\nB)")
    result = result.replace("C)", "\nC)")
    result = result.replace("D)", "\nD)")

    # Ensure the answer section always exists
    if "Answers:" not in result:
        result += "\n\nAnswers:\n1.\n2.\n3."

    return result    