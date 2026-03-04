"""
retriever.py — Hybrid BM25 + FAISS retrieval for ZX Bank Assistant
"""

import numpy as np
import logger
from config import TOP_K_RETRIEVAL, TOP_K_FINAL, RETRIEVAL_THRESHOLD
from ingest import get_index, get_model


def _normalize(scores: list[float]) -> list[float]:
    """Min-max normalization to [0, 1]."""
    if not scores:
        return scores
    min_s = min(scores)
    max_s = max(scores)
    if max_s == min_s:
        return [1.0] * len(scores)
    return [(s - min_s) / (max_s - min_s) for s in scores]


def retrieve(query: str) -> tuple[list[dict], str]:
    """
    Hybrid BM25 + FAISS retrieval.
    Returns (top_chunks_with_scores, confidence: "HIGH" | "LOW").
    """
    faiss_index, bm25, chunks = get_index()
    model = get_model()

    total_chunks = len(chunks)
    k = min(TOP_K_RETRIEVAL, total_chunks)

    # ── 1. Semantic (FAISS) Search ───────────────────────────────────────────
    query_embedding = model.encode([query], normalize_embeddings=True)
    query_embedding = np.array(query_embedding, dtype="float32")

    faiss_scores, faiss_indices = faiss_index.search(query_embedding, k)
    faiss_scores = faiss_scores[0].tolist()
    faiss_indices = faiss_indices[0].tolist()

    # ── 2. BM25 Search ───────────────────────────────────────────────────────
    tokenized_query = query.lower().split()
    bm25_raw_scores = bm25.get_scores(tokenized_query)

    # Get top-k BM25 indices
    bm25_top_indices = np.argsort(bm25_raw_scores)[::-1][:k].tolist()
    bm25_top_scores = [bm25_raw_scores[i] for i in bm25_top_indices]

    # ── 3. Normalize Scores ─────────────────────────────────────────────────
    faiss_norm = _normalize(faiss_scores)
    bm25_norm = _normalize(bm25_top_scores)

    # Build dicts: chunk_id → normalized score
    semantic_map: dict[int, float] = {
        faiss_indices[i]: faiss_norm[i] for i in range(len(faiss_indices))
    }
    bm25_map: dict[int, float] = {
        bm25_top_indices[i]: bm25_norm[i] for i in range(len(bm25_top_indices))
    }

    # ── 4. Merge: deduplicate by chunk_id, combined score ──────────────────
    all_ids = set(semantic_map.keys()) | set(bm25_map.keys())
    combined: list[dict] = []
    for cid in all_ids:
        sem_score = semantic_map.get(cid, 0.0)
        bm25_score_val = bm25_map.get(cid, 0.0)
        final = 0.6 * sem_score + 0.4 * bm25_score_val
        combined.append({
            **chunks[cid],
            "semantic_score": round(sem_score, 4),
            "bm25_score": round(bm25_score_val, 4),
            "final_score": round(final, 4),
        })

    # Sort by final score descending
    combined.sort(key=lambda x: -x["final_score"])
    top = combined[:TOP_K_FINAL]

    # ── 5. Log Retrieval ────────────────────────────────────────────────────
    logger.log_retrieval_triggered(top)

    # ── 6. Confidence Check ─────────────────────────────────────────────────
    max_score = top[0]["final_score"] if top else 0.0
    confidence = "HIGH" if max_score >= RETRIEVAL_THRESHOLD else "LOW"
    logger.log_confidence(confidence)

    return top, confidence
