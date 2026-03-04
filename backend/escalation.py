"""
escalation.py — Human escalation state machine and storage for ZX Bank Assistant
"""

import csv
import json
import os
from datetime import datetime, timezone

import logger
import session as sess
from config import ESCALATIONS_JSON_PATH, ESCALATIONS_CSV_PATH, DATA_DIR

CSV_HEADER = ["timestamp", "session_id", "name", "contact", "trigger_query"]


def _ensure_csv():
    """Create the CSV with its header if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(ESCALATIONS_CSV_PATH):
        with open(ESCALATIONS_CSV_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADER)


def _ensure_json():
    """Create the empty escalations JSON if it doesn't exist."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if not os.path.exists(ESCALATIONS_JSON_PATH):
        with open(ESCALATIONS_JSON_PATH, "w", encoding="utf-8") as f:
            json.dump([], f)


def _store(session_id: str, name: str, contact: str, trigger_query: str) -> str:
    """Append escalation record to both JSON and CSV, return ISO timestamp."""
    _ensure_json()
    _ensure_csv()

    timestamp = datetime.now(timezone.utc).isoformat()
    record = {
        "timestamp": timestamp,
        "session_id": session_id,
        "name": name,
        "contact": contact,
        "trigger_query": trigger_query,
    }

    # JSON append
    with open(ESCALATIONS_JSON_PATH, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data.append(record)
        f.seek(0)
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.truncate()

    # CSV append
    with open(ESCALATIONS_CSV_PATH, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADER)
        writer.writerow(record)

    logger.log_escalation(name=name, contact=contact, timestamp=timestamp)
    return timestamp


def handle_escalation(session_id: str, session: dict, message: str) -> str:
    """
    State machine for human escalation.
    State 0 → ask for name
    State 1 → ask for contact
    State 2 → store and confirm
    Returns the bot response string.
    """
    state = sess.get_escalation_state(session)

    if state == 0:
        # Just detected escalation intent — record trigger query from caller context if available
        esc_data = sess.get_escalation_data(session)
        if not esc_data.get("trigger_query"):
            sess.set_escalation_data(session, "trigger_query", message)
        sess.set_escalation_state(session, 1)
        return "Sure! I'll connect you with a human representative. Please provide your full name."

    elif state == 1:
        # Received name
        sess.set_escalation_data(session, "name", message.strip())
        sess.set_escalation_state(session, 2)
        name = message.strip()
        return f"Thank you, {name}. Please provide your contact number so our representative can reach you."

    elif state == 2:
        # Received contact number
        sess.set_escalation_data(session, "contact", message.strip())
        esc_data = sess.get_escalation_data(session)
        name = esc_data.get("name", "")
        contact = esc_data.get("contact", "")
        trigger = esc_data.get("trigger_query", "")

        _store(session_id, name, contact, trigger)
        sess.reset_escalation(session)
        return (
            f"Thank you, {name}! A human representative will call you at {contact} shortly. "
            "Is there anything else I can help you with?"
        )

    else:
        # Safeguard: reset and restart
        sess.reset_escalation(session)
        return "I'm sorry, something went wrong with the escalation flow. Let me restart. How can I help you?"
