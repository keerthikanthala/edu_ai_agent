import os
import random
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_quiz(text, difficulty="Medium", num_questions=3):

    difficulty_rules = {
        "Easy": "Ask simple factual recall questions.",
        "Medium": "Ask conceptual understanding questions.",
        "Hard": "Ask analytical reasoning questions."
    }

    instruction = difficulty_rules.get(difficulty, "")


    if len(text) > 3000:
        start = random.randint(0, len(text) - 3000)
        text = text[start:start + 3000]

    prompt = f"""
Generate EXACTLY {num_questions} quiz questions.

Difficulty: {difficulty}
Instruction: {instruction}

Return ONLY valid JSON in this format:

[
  {{
    "question": "question text",
    "options": ["A", "B", "C", "D"],
    "answer": "A",
    "explanation": "short explanation"
  }}
]

Rules:
- 4 options per question
- answer must be one of the options EXACTLY
- no extra text outside JSON

Study Material:
{text}
"""

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.5
    )

    result = completion.choices[0].message.content

    try:
        return json.loads(result)
    except:
        return []