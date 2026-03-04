"""
session.py — Persistent multi-turn conversation state for ZX Bank Assistant
"""

import uuid
import json
import os
from datetime import datetime, timedelta
from config import SESSION_EXPIRY_MINUTES, MAX_HISTORY_TURNS, SESSIONS_JSON_PATH

# In-memory session store: { session_id: session_dict }
_sessions: dict[str, dict] = {}

def _now() -> datetime:
    return datetime.utcnow()

def _load_sessions():
    global _sessions
    if os.path.exists(SESSIONS_JSON_PATH):
        try:
            with open(SESSIONS_JSON_PATH, "r", encoding="utf-8") as f:
                data = json.load(f)
                for sid, sdata in data.items():
                    sdata["last_active"] = datetime.fromisoformat(sdata["last_active"])
                _sessions = data
        except Exception as e:
            print(f"Error loading sessions: {e}")
            _sessions = {}

def _save_sessions():
    try:
        os.makedirs(os.path.dirname(SESSIONS_JSON_PATH), exist_ok=True)
        data = {}
        for sid, sdata in _sessions.items():
            s_copy = {**sdata}
            s_copy["last_active"] = sdata["last_active"].isoformat()
            data[sid] = s_copy
        
        with open(SESSIONS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error saving sessions: {e}")

# Load on startup
_load_sessions()

def create_session() -> str:
    """Create a new session and return its UUID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "conversation_history": [],   # list of {"role": ..., "content": ...}
        "escalation_state": 0,         # 0 = none, 1 = awaiting name, 2 = awaiting contact
        "escalation_data": {
            "name": None,
            "contact": None,
            "trigger_query": None,
        },
        "last_active": _now(),
    }
    _save_sessions()
    return session_id

def get_session(session_id: str) -> dict | None:
    """Retrieve a session if it exists and has not expired."""
    session = _sessions.get(session_id)
    if session is None:
        return None

    expiry_time = session["last_active"] + timedelta(minutes=SESSION_EXPIRY_MINUTES)
    if _now() > expiry_time:
        # Session expired — remove it
        del _sessions[session_id]
        _save_sessions()
        return None

    session["last_active"] = _now()
    _save_sessions()
    return session

def get_or_create_session(session_id: str | None) -> tuple[str, dict]:
    """Get an existing session or create a new one. Returns (session_id, session)."""
    if session_id:
        session = get_session(session_id)
        if session is not None:
            return session_id, session

    # Create new session
    new_id = create_session()
    return new_id, _sessions[new_id]

def add_message(session: dict, role: str, content: str):
    """Add a message to the conversation history, keeping only the last N turns."""
    session["conversation_history"].append({"role": role, "content": content})

    # Sliding window: each turn = 1 user + 1 assistant message
    max_messages = MAX_HISTORY_TURNS * 2
    if len(session["conversation_history"]) > max_messages:
        session["conversation_history"] = session["conversation_history"][-max_messages:]
    
    _save_sessions()

def get_history(session: dict) -> list[dict]:
    """Return the conversation history for LLM context."""
    return session["conversation_history"]

def get_escalation_state(session: dict) -> int:
    return session["escalation_state"]

def set_escalation_state(session: dict, state: int):
    session["escalation_state"] = state
    _save_sessions()

def get_escalation_data(session: dict) -> dict:
    return session["escalation_data"]

def set_escalation_data(session: dict, key: str, value: str):
    session["escalation_data"][key] = value
    _save_sessions()

def reset_escalation(session: dict):
    session["escalation_state"] = 0
    session["escalation_data"] = {"name": None, "contact": None, "trigger_query": None}
    _save_sessions()

def get_all_sessions() -> dict:
    """Return all active (non-expired) sessions."""
    _purge_expired()
    return _sessions

def _purge_expired():
    """Remove all expired sessions."""
    expired = [
        sid for sid, s in _sessions.items()
        if _now() > s["last_active"] + timedelta(minutes=SESSION_EXPIRY_MINUTES)
    ]
    if expired:
        for sid in expired:
            del _sessions[sid]
        _save_sessions()
