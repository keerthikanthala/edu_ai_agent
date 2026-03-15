import os
import random
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

api_key = os.getenv("GROQ_API_KEY")
client = Groq(api_key=api_key)


def generate_quiz(text, difficulty="Medium", num_questions=3):

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

Generate EXACTLY {num_questions} multiple choice questions from the study material.

Difficulty: {difficulty}
Instruction: {difficulty_instruction}

STRICT RULES:
- Each question must have 4 options.
- Each option must be on its own line.
- Label options exactly A) B) C) D).
- Distribute correct answers evenly across A, B, C, and D.
- Avoid having the same correct option repeated more than twice in a row.
- Do NOT show the answer under the question.
- At the very end provide an answer key.
- After the answer key, provide short explanations for each correct answer.
- Each question must test a different concept from the study material.
- Avoid repeating the same topic.


Study Material:
{text}

Output format:

Question 1:
A)
B)
C)
D)

Continue until Question {num_questions}.

Answers:
1. A
2. B

Explanations:
1. explanation
2. explanation
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    result = completion.choices[0].message.content
    # Randomize answer letters safely
    
    letters = ["A", "B", "C", "D"]
    lines = result.split("\n")

    inside_answers = False

    for i, line in enumerate(lines):

        if "Answers" in line:
            inside_answers = True
            continue

        if "Explanation" in line:
            inside_answers = False

        if inside_answers and "." in line:
            parts = line.split(".")
            if parts[0].strip().isdigit():
                number = parts[0].strip()
                lines[i] = f"{number}. {random.choice(letters)}"

    result = "\n".join(lines)

    # Fix compressed options (safe version)
    result = result.replace(" A)", "\nA)")
    result = result.replace(" B)", "\nB)")
    result = result.replace(" C)", "\nC)")
    result = result.replace(" D)", "\nD)")
    result = result.replace("A)", "\nA)")
    result = result.replace("B)", "\nB)")
    result = result.replace("C)", "\nC)")
    result = result.replace("D)", "\nD)")


    # Ensure explanations appear cleanly
    result = result.replace("Explanations:", "\nExplanations:\n")

    return result
     