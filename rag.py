# rag.py
# Retrieval-Augmented Generation with caching + re-ranking

from sentence_transformers import SentenceTransformer, CrossEncoder
import faiss
import numpy as np

# Cache models
_model = None
_cross_encoder = None
_index = None
_chunks = None

def load_models():
    global _model, _cross_encoder
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")   # fast embeddings
    if _cross_encoder is None:
        _cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")  # re-ranker
    return _model, _cross_encoder

def build_index(chunks):
    """Build FAISS index once per document upload"""
    global _index, _chunks
    _chunks = chunks
    model, _ = load_models()
    embeddings = model.encode(chunks)
    _index = faiss.IndexFlatL2(embeddings.shape[1])
    _index.add(np.array(embeddings))

def get_relevant_chunks(chunks, query, top_k=5):
    """Retrieve top_k relevant chunks for a query with re-ranking"""
    global _index, _chunks
    model, cross_encoder = load_models()

    # Build index only if chunks changed or not built yet
    if _index is None or _chunks != chunks:
        build_index(chunks)

    # Encode query
    query_emb = model.encode([query])
    distances, indices = _index.search(np.array(query_emb), top_k)
    candidate_chunks = [chunks[i] for i in indices[0] if i < len(chunks)]

    # Re-rank candidates using cross-encoder
    pairs = [(query, chunk) for chunk in candidate_chunks]
    scores = cross_encoder.predict(pairs)

    # Sort chunks by score (highest relevance first)
    ranked_chunks = [chunk for _, chunk in sorted(zip(scores, candidate_chunks), key=lambda x: x[0], reverse=True)]

    return ranked_chunks
