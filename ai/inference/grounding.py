"""Ground model output in evidence from the user's original text."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

EVENT_TYPES = {
    "quotation",
    "payment",
    "meeting",
    "call",
    "message",
    "email",
    "appointment",
    "order",
    "delivery",
    "document",
    "project",
    "service",
    "visit",
    "complaint",
    "proposal",
    "other",
}

STATUS_BY_TERMS = {
    "cancelled": ("cancel", "cancelled", "canceled"),
    "completed": ("completed", "complete", "done", "sent", "bhej diya", "ho gaya"),
    "pending": ("pending", "wait", "waiting", "baaki"),
    "planned": ("scheduled", "schedule", "planned", "plan", "tay"),
}

ACTION_TERMS = {
    "call": ("call", "phone", "फोन"),
    "message": ("message", "msg", "संदेश"),
    "email": ("email", "e-mail", "mail"),
}

DATE_PATTERN = re.compile(
    r"\b(?:today|tomorrow|yesterday|tonight|friday|monday|tuesday|wednesday|"
    r"thursday|saturday|sunday|kal|aaj|आज|कल|parso|परसों|अगले हफ्ते|next week)"
    r"(?:\s+(?:\d{1,2}(?::\d{2})?\s*(?:am|pm|बजे)?))?"
    r"(?:\s*बजे)?",
    re.IGNORECASE,
)


def _text_contains(text: str, value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip()) and value.casefold() in text.casefold()


def _first_term(text: str, terms: tuple[str, ...]) -> bool:
    lowered = text.casefold()
    return any(term.casefold() in lowered for term in terms)


def _event_type(text: str, candidate: Any) -> str | None:
    if isinstance(candidate, str) and candidate.casefold() in EVENT_TYPES:
        return candidate.casefold()
    for event_type in EVENT_TYPES - {"other"}:
        if _text_contains(text, event_type):
            return event_type
    return None


def _status(text: str, candidate: Any) -> str | None:
    if isinstance(candidate, str) and candidate.casefold() in {"planned", "completed", "pending", "cancelled", "unknown"}:
        return candidate.casefold()
    for status, terms in STATUS_BY_TERMS.items():
        if _first_term(text, terms):
            return status
    return None


def _date_expression(text: str, candidate: Any) -> str | None:
    if _text_contains(text, candidate):
        return candidate.strip()
    match = DATE_PATTERN.search(text)
    if not match:
        return None
    end = match.end()
    remainder = text[end:].lstrip()
    for time_word in ("बजे", "baje"):
        if remainder.startswith(time_word):
            end += len(text[end:]) - len(remainder) + len(time_word)
            break
    return text[match.start() : end].strip()


def ground_result(text: str, result: dict[str, Any]) -> dict[str, Any]:
    """Remove values that have no textual evidence in the user input."""
    grounded = deepcopy(result)
    
    if not isinstance(grounded.get("contact"), dict):
        grounded["contact"] = {}
    if not isinstance(grounded.get("event"), dict):
        grounded["event"] = {}
    if not isinstance(grounded.get("followup"), dict):
        grounded["followup"] = {}

    contact = grounded["contact"]
    event = grounded["event"]
    followup = grounded["followup"]

    for field in ("name", "organization"):
        if not _text_contains(text, contact.get(field)):
            contact[field] = None

    event["type"] = _event_type(text, event.get("type"))
    if not _text_contains(text, event.get("description")):
        event["description"] = None
    if event.get("amount") is not None and not re.search(r"\d", text):
        event["amount"] = None
    event["status"] = _status(text, event.get("status"))

    followup_required = bool(followup.get("required"))
    followup["required"] = followup_required
    followup["action"] = followup.get("action") if followup_required else None
    
    if not followup_required:
        followup["date_expression"] = None
    else:
        followup["date_expression"] = _date_expression(text, followup.get("date_expression"))
        
    return grounded
