"""
logger.py — Structured terminal logging for ZX Bank Assistant
"""

import sys

DIVIDER = "═" * 52


def log_query_start(session_id: str, query: str):
    print(f"\n{DIVIDER}", flush=True)
    print(f"[SESSION] {session_id}", flush=True)
    print(f'[QUERY]   "{query}"', flush=True)


def log_intent(intent: str):
    print(f"[INTENT]  {intent}", flush=True)


def log_retrieval_skipped():
    print("[RETRIEVAL] SKIPPED", flush=True)


def log_retrieval_triggered(chunks: list):
    print("[RETRIEVAL] TRIGGERED", flush=True)
    for i, chunk in enumerate(chunks, 1):
        source = chunk.get("source", "unknown")
        section = chunk.get("section", "unknown")
        score = chunk.get("final_score", 0.0)
        print(f"  → Chunk {i}: {source} | Section: {section} | Score: {score:.2f}", flush=True)


def log_confidence(confidence: str):
    print(f"[CONFIDENCE] {confidence}", flush=True)


def log_llm_call(called: bool, model: str = "", tokens_est: int = 0):
    if called:
        print(f"[LLM CALL] YES | model: {model} | tokens_est: ~{tokens_est}", flush=True)
    else:
        print("[LLM CALL] NO (canned/hardcoded response)", flush=True)


def log_response_path(path: str):
    print(f"[RESPONSE PATH] {path}", flush=True)


def log_escalation(name: str, contact: str, timestamp: str):
    print(f"[ESCALATION] TRIGGERED", flush=True)
    print(f"[STORED] Name: {name} | Contact: {contact} | Time: {timestamp}", flush=True)


def log_adversarial(pattern: str):
    print(f'[ADVERSARIAL] BLOCKED | Pattern matched: "{pattern}"', flush=True)


def log_query_end():
    print(DIVIDER, flush=True)
