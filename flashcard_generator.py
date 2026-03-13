def generate_flashcards(text):
    flashcards = []
    sentences = text.split(".")
    
    for s in sentences:
        s = s.strip()
        if s:
            flashcards.append({
                "question": f"What is meant by: {s}?",
                "answer": s
            })

    return flashcards 