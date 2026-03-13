import os
import random
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def generate_quiz(text, difficulty="Medium", num_questions=3):

    # Difficulty-aware quiz generation
    difficulty_rules = {
        "Easy": "Ask simple factual recall questions directly based on the text.",
        "Medium": "Ask conceptual questions that require understanding of the material.",
        "Hard": "Ask analytical or reasoning-based questions that test deeper understanding."
    }

    difficulty_instruction = difficulty_rules.get(difficulty, "")

    # Random document section selection
    if len(text) > 3000:
        start = random.randint(0, len(text) - 3000)
        text = text[start:start + 3000]

    prompt = f"""
You are an AI quiz generator.

Generate {num_questions} multiple choice questions from the study material.

The quiz should increase in difficulty progressively:
- Question 1 should be Easy
- Question 2 should be Medium
- Question 3 should be Hard

Difficulty guidelines:
Easy: simple factual recall from the text.
Medium: conceptual understanding questions.
Hard: analytical or reasoning-based questions.

STRICT RULES:
- Each question must have 4 options.
- Each option must be on its own line.
- Label options exactly A) B) C) D).
- Do NOT show the answer under the question.
- At the very end provide an answer key.
- After the answer key, provide short explanations for each correct answer.
- Each question must test a different concept from the study material.
- Avoid repeating the same topic or idea in multiple questions.

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
1.
2.
3.

Explanations:
1.
2.
3.
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

    # Ensure answer section exists
    if "Answers:" not in result:
        result += "\n\nAnswers:\n1.\n2.\n3."

    # Ensure explanations section exists
    if "Explanations:" not in result:
        result += "\n\nExplanations:\n1.\n2.\n3."

    return result