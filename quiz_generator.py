# quiz_generator.py
import os
import random
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _safe_json_load(text):
    try:
        return json.loads(text)
    except Exception:
        # try to extract first JSON block
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except Exception:
                return None
    return None

def generate_quiz(text, difficulty="Medium", num_questions=3, max_chars=3000):
    difficulty_rules = {
        "Easy": "Ask simple factual recall questions.",
        "Medium": "Ask conceptual understanding questions.",
        "Hard": "Ask analytical reasoning questions."
    }
    instruction = difficulty_rules.get(difficulty, "")

    # limit text size for prompt
    if len(text) > max_chars:
        start = random.randint(0, max(0, len(text) - max_chars))
        text = text[start:start + max_chars]

    prompt = f"""
Generate EXACTLY {num_questions} quiz questions.

Difficulty: {difficulty}
Instruction: {instruction}

Return ONLY valid JSON in this format:

[
  {{
    "question": "question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "answer": "Option A",
    "explanation": "short explanation",
    "source_chunk": 5
  }}
]

Rules:
- 4 options per question
- answer must match one of the options exactly
- include source_chunk (approximate chunk index) if possible
- no extra text outside JSON

Study Material:
{text}
"""

    for attempt in range(3):
        try:
            completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            raw = completion.choices[0].message.content
            parsed = _safe_json_load(raw)
            if parsed and isinstance(parsed, list) and len(parsed) >= 1:
                return _normalize_questions(parsed, difficulty)
            # if parsing failed, retry
        except Exception:
            time.sleep(1)
    # fallback generator
    return _fallback_quiz(num_questions, difficulty)

def _normalize_questions(questions, default_difficulty):
    normalized = []
    for q in questions:
        qtext = q.get("question", "").strip()
        opts = q.get("options", [])[:4]
        # ensure 4 options
        if len(opts) < 4:
            # pad with placeholders (should rarely happen)
            opts = opts + [f"Option {chr(65+i)}" for i in range(4 - len(opts))]
        # shuffle while tracking correct index
        correct_text = q.get("answer", opts[0])
        paired = list(enumerate(opts))
        random.shuffle(paired)
        shuffled_opts = [opt for _, opt in paired]
        try:
            correct_index = shuffled_opts.index(correct_text)
        except ValueError:
            # try matching by normalized text
            lowered = [o.strip().lower() for o in shuffled_opts]
            try:
                correct_index = lowered.index(correct_text.strip().lower())
            except Exception:
                correct_index = 0
        normalized.append({
            "question": qtext,
            "options": shuffled_opts,
            "correct_index": correct_index,
            "difficulty": q.get("difficulty", default_difficulty),
            "explanation": q.get("explanation", ""),
            "source_chunk": q.get("source_chunk", None)
        })
    return normalized

def _fallback_quiz(n, difficulty):
    return [
        {
            "question": f"Sample Question {i+1}",
            "options": ["Option A", "Option B", "Option C", "Option D"],
            "correct_index": 0,
            "difficulty": difficulty,
            "explanation": "Fallback explanation due to API failure.",
            "source_chunk": None
        }
        for i in range(n)
    ]