"""
main.py — FastAPI application for ZX Bank Conversational AI Assistant
"""

from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

import logger
import session as sess
import classifier
import retriever
import responder
import escalation
from ingest import ensure_index


from fastapi.middleware.cors import CORSMiddleware

# ─── App Lifecycle ────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run ingestion on startup if index does not exist."""
    ensure_index()
    yield


app = FastAPI(
    title="ZX Bank Conversational AI",
    description="Production-ready RAG-based banking assistant with hybrid retrieval.",
    version="1.0.0",
    lifespan=lifespan,
)

# Set up CORS for Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─── Request / Response Models ────────────────────────────────────────────────

class ChatRequest(BaseModel):
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    session_id: str
    response: str
    intent: str
    retrieval_triggered: bool
    retrieved_docs: list[str]
    confidence: str
    citations: list[str]
    escalation_triggered: bool


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    session = sess.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    return {
        "session_id": session_id,
        "conversation_history": sess.get_history(session),
        "escalation_state": sess.get_escalation_state(session),
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    message = req.message.strip()
    if not message:
        raise HTTPException(status_code=422, detail="Message cannot be empty")

    # ── Session Management ────────────────────────────────────────────────────
    session_id, session = sess.get_or_create_session(req.session_id)

    # ── Logging Header ────────────────────────────────────────────────────────
    logger.log_query_start(session_id, message)

    # ── Escalation State Machine (takes priority if already in flow) ─────────
    escalation_state = sess.get_escalation_state(session)
    if escalation_state > 0:
        # We are mid-escalation flow — route directly to escalation handler
        logger.log_intent("ESCALATION")
        response_text = escalation.handle_escalation(session_id, session, message)
        sess.add_message(session, "user", message)
        sess.add_message(session, "assistant", response_text)
        logger.log_llm_call(called=False)
        logger.log_response_path("ESCALATION_FLOW")
        logger.log_query_end()
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            intent="ESCALATION",
            retrieval_triggered=False,
            retrieved_docs=[],
            confidence="N/A",
            citations=[],
            escalation_triggered=True,
        )

    # ── Intent Classification ─────────────────────────────────────────────────
    intent, matched_pattern = classifier.classify(message)

    # ── Route by Intent ───────────────────────────────────────────────────────

    if intent == "ADVERSARIAL":
        response_text, llm_called = responder.respond_adversarial()
        sess.add_message(session, "user", message)
        sess.add_message(session, "assistant", response_text)
        logger.log_query_end()
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            intent="ADVERSARIAL",
            retrieval_triggered=False,
            retrieved_docs=[],
            confidence="N/A",
            citations=[],
            escalation_triggered=False,
        )

    elif intent == "ESCALATION":
        # Record trigger query, then let handle_escalation advance from state 0 → 1
        sess.set_escalation_data(session, "trigger_query", message)
        response_text = escalation.handle_escalation(session_id, session, message)
        sess.add_message(session, "user", message)
        sess.add_message(session, "assistant", response_text)
        logger.log_llm_call(called=False)
        logger.log_response_path("ESCALATION_TRIGGERED")
        logger.log_query_end()
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            intent="ESCALATION",
            retrieval_triggered=False,
            retrieved_docs=[],
            confidence="N/A",
            citations=[],
            escalation_triggered=True,
        )

    elif intent == "SMALL_TALK":
        logger.log_retrieval_skipped()
        history = sess.get_history(session)
        response_text, llm_called = responder.respond_small_talk(message, history)
        sess.add_message(session, "user", message)
        sess.add_message(session, "assistant", response_text)
        logger.log_query_end()
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            intent="SMALL_TALK",
            retrieval_triggered=False,
            retrieved_docs=[],
            confidence="N/A",
            citations=[],
            escalation_triggered=False,
        )

    else:  # DOCUMENT_QUERY
        # Retrieval
        chunks, confidence = retriever.retrieve(message)
        retrieved_docs = list({c["source"] for c in chunks})

        # Response generation
        history = sess.get_history(session)
        response_text, llm_called, citations = responder.respond_document_query(
            message, chunks, confidence, history
        )

        sess.add_message(session, "user", message)
        sess.add_message(session, "assistant", response_text)
        logger.log_query_end()
        return ChatResponse(
            session_id=session_id,
            response=response_text,
            intent="DOCUMENT_QUERY",
            retrieval_triggered=True,
            retrieved_docs=retrieved_docs,
            confidence=confidence,
            citations=citations,
            escalation_triggered=False,
        )
