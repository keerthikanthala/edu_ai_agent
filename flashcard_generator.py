import os
import json
import time
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def generate_flashcards(text, difficulty="Medium", num_flashcards=12):

    chunk_size = 1500
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    all_cards = []

    for chunk in chunks[:3]:  # limit to avoid rate limit

        prompt = f"""
Create 4 flashcards from this text.

Return ONLY JSON:

[
  {{
    "front": "question",
    "back": "answer"
  }}
]

Study Material:
{chunk}
"""

        # retry logic
        for attempt in range(3):
            try:
                completion = client.chat.completions.create(
                    model="llama-3.1-8b-instant",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.5
                )
                break
            except Exception:
                time.sleep(2)
        else:
            continue

        result = completion.choices[0].message.content

        try:
            cards = json.loads(result)
            all_cards.extend(cards)
        except:
            continue

    return all_cards[:num_flashcards]