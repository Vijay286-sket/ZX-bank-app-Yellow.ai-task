"""
responder.py — LLM response generation via OpenRouter for ZX Bank Assistant
"""

import re
from google import genai
import logger
from config import GEMINI_API_KEY, LLM_MODEL

SYSTEM_PROMPT = (
    "You are ZX Bank's official virtual assistant. "
    "Answer the user's question clearly and concisely based ONLY on the provided documents. "
    "If the answer is not in the documents, say so clearly and do not fabricate information. "
    "Format your final answer neatly, starting with a summary, followed by a detailed answer, "
    "and finally a 'Sources' section listing the source filenames used."
)

ADVERSARIAL_RESPONSE = (
    "I'm unable to process that request. "
    "If you need banking assistance, please ask a legitimate question."
)

LOW_CONFIDENCE_RESPONSE = (
    "I don't have sufficient information in my knowledge base to answer that confidently. "
    "Would you like me to escalate this to a human representative?"
)

SMALL_TALK_CANNED: dict[str, str] = {
    r"\bhello\b|\bhi\b|\bhey\b": "Hello! Welcome to ZX Bank. How can I assist you today?",
    r"how are you": "I'm doing great, thank you! I'm here to help with all your ZX Bank queries.",
    r"what can you do|what do you do": (
        "I can help you with account information, transfers, loan inquiries, ATM locations, "
        "fraud reporting, KYC verification, and much more. Just ask!"
    ),
    r"who are you": "I'm the ZX Bank Virtual Assistant, here to help you with your banking needs 24/7.",
    r"tell me a joke": "Why don't banks tell jokes? Because they'd lose interest! 😄",
    r"\bthanks\b|\bthank you\b": "You're welcome! Is there anything else I can help you with?",
    r"\bbye\b|\bgoodbye\b": "Goodbye! Have a wonderful day. Feel free to reach out anytime.",
    r"good (morning|afternoon|evening|night)": "Good day! How can ZX Bank assist you today?",
}


def _canned_response(message: str) -> str | None:
    lowered = message.lower().strip()
    for pattern, response in SMALL_TALK_CANNED.items():
        if re.search(pattern, lowered):
            return response
    return None


def _call_llm(messages: list[dict], est_tokens: int = 500) -> str:
    """Make a call to Gemini API using google-genai."""
    logger.log_llm_call(called=True, model=LLM_MODEL, tokens_est=est_tokens)
    
    # We serialize the message history into a single string prompt
    prompt_parts = []
    for msg in messages:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "system":
            prompt_parts.append(f"System Instructions:\n{content}\n")
        elif role == "user":
            prompt_parts.append(f"User: {content}\n")
        elif role == "assistant":
            prompt_parts.append(f"Assistant: {content}\n")
            
    prompt = "\n".join(prompt_parts)

    client = genai.Client(api_key=GEMINI_API_KEY)
    response = client.models.generate_content(
        model=LLM_MODEL,
        contents=prompt,
    )

    return response.text.strip() if response.text else "I'm sorry, my language model failed to generate a response."


def respond_small_talk(message: str, history: list[dict]) -> tuple[str, bool]:
    """
    Return a response for SMALL_TALK intent.
    Returns (response_text, llm_called).
    """
    canned = _canned_response(message)
    if canned:
        logger.log_llm_call(called=False)
        logger.log_response_path("SMALL_TALK_CANNED")
        return canned, False

    # Fallback: minimal LLM call (no retrieval, no system docs)
    messages = [
        {"role": "system", "content": "You are a friendly ZX Bank virtual assistant. Keep responses brief."},
        {"role": "user", "content": message},
    ]
    response = _call_llm(messages, est_tokens=180)
    logger.log_response_path("SMALL_TALK_LLM")
    return response, True


def respond_adversarial() -> tuple[str, bool]:
    """Return hardcoded refusal for adversarial queries. No LLM call."""
    logger.log_llm_call(called=False)
    logger.log_response_path("ADVERSARIAL_BLOCKED")
    return ADVERSARIAL_RESPONSE, False


def respond_document_query(
    query: str,
    chunks: list[dict],
    confidence: str,
    history: list[dict],
) -> tuple[str, bool, list[str]]:
    """
    Return a grounded LLM response for DOCUMENT_QUERY.
    Returns (response_text, llm_called, citations).
    """
    if confidence == "LOW" or not chunks:
        logger.log_llm_call(called=False)
        logger.log_response_path("LOW_CONFIDENCE_FALLBACK")
        return LOW_CONFIDENCE_RESPONSE, False, []

    # Format retrieved chunks as context
    context_parts = []
    citations = []
    for chunk in chunks:
        source = chunk.get("source", "unknown")
        section = chunk.get("section", "")
        text = chunk.get("text", "")
        context_parts.append(f"[Source: {source} | Section: {section}]\n{text}")
        if source not in citations:
            citations.append(source)

    context_str = "\n\n---\n\n".join(context_parts)
    user_content = f"{context_str}\n\nUser question: {query}"

    # Build messages (include brief history for multi-turn context)
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    # Add last 4 history turns (2 user + 2 assistant) for context
    short_history = history[-8:] if len(history) > 8 else history
    messages.extend(short_history[:-1] if short_history else [])  # Exclude current user msg (added below)
    messages.append({"role": "user", "content": user_content})

    est_tokens = sum(len(c["text"].split()) for c in chunks) + len(query.split()) + 150
    response = _call_llm(messages, est_tokens=est_tokens)
    logger.log_response_path("DOCUMENT_GROUNDED")
    return response, True, citations
