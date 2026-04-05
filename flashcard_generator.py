# flashcard_generator.py
import os
import json
import time
import random
from dotenv import load_dotenv
from groq import Groq
import re

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def _safe_json_load(text):
    try:
        return json.loads(text)
    except Exception:
        start = text.find('[')
        end = text.rfind(']') + 1
        if start != -1 and end != -1:
            try:
                return json.loads(text[start:end])
            except Exception:
                return None
    return None

def _normalize_text(s):
    s = s.strip().lower()
    s = re.sub(r'\s+', ' ', s)
    s = re.sub(r'[^\w\s]', '', s)
    return s

def generate_flashcards(text, difficulty="Medium", num_flashcards=12, chunk_size=1500):
    # chunk text
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    all_cards = []
    seen = set()

    for idx, chunk in enumerate(chunks[:6]):  # limit chunks to avoid rate limits
        prompt = f"""
Create up to 6 concise flashcards from the study material below.
Return ONLY valid JSON array of objects with keys: front, back.
Include short answers and avoid verbatim long paragraphs.

Study Material:
{chunk}
"""
        for attempt in range(3):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.4
                )
                raw = completion.choices[0].message.content
                parsed = _safe_json_load(raw)
                if not parsed:
                    time.sleep(1)
                    continue
                for card in parsed:
                    front = card.get("front", "").strip()
                    back = card.get("back", "").strip()
                    if not front or not back:
                        continue
                    key = _normalize_text(front)
                    if key in seen:
                        continue
                    seen.add(key)
                    all_cards.append({
                        "front": front,
                        "back": back,
                        "difficulty": difficulty,
                        "source_chunk": idx
                    })
                    if len(all_cards) >= num_flashcards:
                        return all_cards[:num_flashcards]
                break
            except Exception:
                time.sleep(1)
                continue
    # fallback: simple extraction heuristics
    if not all_cards:
        sentences = re.split(r'(?<=[.!?])\s+', text)[:num_flashcards*2]
        for i in range(0, len(sentences), 2):
            if len(all_cards) >= num_flashcards:
                break
            front = sentences[i].strip()[:200]
            back = sentences[i+1].strip()[:300] if i+1 < len(sentences) else "See document."
            key = _normalize_text(front)
            if key in seen:
                continue
            seen.add(key)
            all_cards.append({"front": front, "back": back, "difficulty": difficulty, "source_chunk": None})
    return all_cards[:num_flashcards]