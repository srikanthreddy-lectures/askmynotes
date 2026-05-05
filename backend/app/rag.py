"""Chunking, embedding, and retrieval. In-memory store, one document at a time."""
from __future__ import annotations
import numpy as np
from sentence_transformers import SentenceTransformer

_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None

_chunks: list[str] = []
_embeddings: np.ndarray | None = None  # shape (N, 384), L2-normalized

def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model

def chunk_text(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Sliding-window chunking. We use character windows (not tokens) for
    simplicity and stability — chunk SIZE is the curriculum-chosen tradeoff:
    roughly one paragraph per chunk, with overlap to capture sentences split
    across boundaries."""
    if size <= overlap:
        raise ValueError("size must be greater than overlap")
    chunks: list[str] = []
    i = 0
    step = size - overlap
    while i < len(text):
        piece = text[i : i + size].strip()
        if piece:
            chunks.append(piece)
        i += step
    return chunks

def index_text(text: str) -> int:
    """Replace the store with chunks of the given text. Returns chunk count."""
    global _chunks, _embeddings
    _chunks = chunk_text(text)
    if not _chunks:
        _embeddings = None
        return 0
    model = _get_model()
    embs = model.encode(_chunks, convert_to_numpy=True, normalize_embeddings=True)
    _embeddings = embs.astype(np.float32)
    return len(_chunks)

def retrieve(query: str, k: int = 3) -> list[tuple[str, float]]:
    """Cosine similarity via dot product (embeddings already normalized)."""
    if _embeddings is None or not _chunks:
        return []
    model = _get_model()
    q = model.encode([query], convert_to_numpy=True, normalize_embeddings=True)[0]
    scores = _embeddings @ q  # shape (N,)
    k = min(k, len(_chunks))
    top_idx = np.argsort(-scores)[:k]
    return [(_chunks[i], float(scores[i])) for i in top_idx]

def store_size() -> int:
    return len(_chunks)

def clear() -> None:
    global _chunks, _embeddings
    _chunks = []
    _embeddings = None
