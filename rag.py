def get_relevant_chunks(chunks, query, top_k=5):
    scored_chunks = []

    for chunk in chunks:
        score = chunk.lower().count(query.lower())
        scored_chunks.append((chunk, score))

    scored_chunks.sort(key=lambda x: x[1], reverse=True)

    selected_chunks = [chunk for chunk, score in scored_chunks[:top_k]]

    return selected_chunks