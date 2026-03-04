"""
ingest.py — Document loading, chunking, embedding, and index building for ZX Bank Assistant
"""

import os
import json
import re
import numpy as np
import frontmatter
import faiss
import logger

from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from config import DOCS_DIR, DATA_DIR, FAISS_INDEX_PATH, CHUNKS_JSON_PATH

# ── Globals (loaded once into memory after build) ─────────────────────────────
_model: SentenceTransformer | None = None
_faiss_index: faiss.IndexFlatIP | None = None
_bm25: BM25Okapi | None = None
_chunks: list[dict] = []


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        print("[INGEST] Loading sentence-transformer model…", flush=True)
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def _parse_markdown(filepath: str, filename: str) -> list[dict]:
    """Parse a markdown file into per-section chunks using ## headings."""
    with open(filepath, "r", encoding="utf-8") as f:
        raw = f.read()

    post = frontmatter.loads(raw)
    meta = dict(post.metadata)
    content = post.content

    # Split on ## headings (section-level)
    sections = re.split(r"(?m)^## ", content)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        lines = section.splitlines()
        heading = lines[0].strip()
        text = "\n".join(lines[1:]).strip()
        if not text:
            continue
        chunks.append({
            "source": filename,
            "section": heading,
            "text": text,
            "title": meta.get("title", ""),
            "category": meta.get("category", ""),
            "doc_type": meta.get("doc_type", ""),
            "keywords": [],   # filled in post-processing
        })

    return chunks


def _extract_keywords(chunks: list[dict]) -> list[dict]:
    """Use TF-IDF across all chunks to extract top 5 keywords per chunk."""
    texts = [c["text"] for c in chunks]
    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    tfidf_matrix = vectorizer.fit_transform(texts)
    feature_names = vectorizer.get_feature_names_out()

    for i, chunk in enumerate(chunks):
        row = tfidf_matrix[i]
        scores = zip(row.indices, row.data)
        top_indices = sorted(scores, key=lambda x: -x[1])[:5]
        keywords = [feature_names[idx] for idx, _ in top_indices]
        chunk["keywords"] = keywords

    return chunks


def _build_indices(chunks: list[dict]) -> tuple[faiss.IndexFlatIP, BM25Okapi]:
    """Build FAISS and BM25 indices from chunks."""
    model = _get_model()
    texts = [c["text"] for c in chunks]

    print(f"[INGEST] Encoding {len(texts)} chunks with sentence-transformers…", flush=True)
    embeddings = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    embeddings = np.array(embeddings, dtype="float32")

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # Inner product on normalized vectors = cosine similarity
    index.add(embeddings)

    # BM25
    tokenized = [t.lower().split() for t in texts]
    bm25 = BM25Okapi(tokenized)

    return index, bm25


def build_index():
    """Run full ingestion pipeline and persist results."""
    global _faiss_index, _bm25, _chunks

    os.makedirs(DATA_DIR, exist_ok=True)

    # Collect all markdown files
    all_chunks = []
    for filename in sorted(os.listdir(DOCS_DIR)):
        if filename.endswith(".md"):
            filepath = os.path.join(DOCS_DIR, filename)
            chunks = _parse_markdown(filepath, filename)
            all_chunks.extend(chunks)
            print(f"[INGEST] Parsed '{filename}': {len(chunks)} sections", flush=True)

    if not all_chunks:
        raise RuntimeError(f"No markdown files found in '{DOCS_DIR}'")

    # Add chunk IDs
    for i, chunk in enumerate(all_chunks):
        chunk["chunk_id"] = i

    # Extract TF-IDF keywords
    all_chunks = _extract_keywords(all_chunks)

    # Build indices
    faiss_index, bm25 = _build_indices(all_chunks)

    # Persist FAISS index
    faiss.write_index(faiss_index, FAISS_INDEX_PATH)
    print(f"[INGEST] FAISS index saved → {FAISS_INDEX_PATH}", flush=True)

    # Persist chunks metadata (JSON-serialisable only)
    with open(CHUNKS_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=2, ensure_ascii=False)
    print(f"[INGEST] Chunks metadata saved → {CHUNKS_JSON_PATH}", flush=True)

    _faiss_index = faiss_index
    _bm25 = bm25
    _chunks = all_chunks

    print(f"[INGEST] Done. Total chunks: {len(all_chunks)}", flush=True)


def load_index():
    """Load persisted indices into memory."""
    global _faiss_index, _bm25, _chunks

    with open(CHUNKS_JSON_PATH, "r", encoding="utf-8") as f:
        _chunks = json.load(f)

    _faiss_index = faiss.read_index(FAISS_INDEX_PATH)

    tokenized = [c["text"].lower().split() for c in _chunks]
    _bm25 = BM25Okapi(tokenized)

    print(f"[INGEST] Loaded {len(_chunks)} chunks from disk.", flush=True)


def ensure_index():
    """Load index if it exists, otherwise build it."""
    if os.path.exists(FAISS_INDEX_PATH) and os.path.exists(CHUNKS_JSON_PATH):
        print("[INGEST] Existing index found. Loading…", flush=True)
        load_index()
    else:
        print("[INGEST] No index found. Building from scratch…", flush=True)
        build_index()


def get_index():
    """Return (faiss_index, bm25, chunks) — must call ensure_index() first."""
    return _faiss_index, _bm25, _chunks


def get_model() -> SentenceTransformer:
    return _get_model()
