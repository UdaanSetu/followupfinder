"""Safe parsing of model-generated JSON."""

from __future__ import annotations

import json
import re
from typing import Any


class InferenceParseError(ValueError):
    """Raised when model output does not contain a valid JSON object."""


def parse_model_output(text: str) -> dict[str, Any]:
    """Parse a JSON object from plain output or an accidental code fence."""
    if not isinstance(text, str):
        raise InferenceParseError("Model output must be text")

    cleaned = text.strip()
    if "</think>" in cleaned:
        cleaned = cleaned.split("</think>", 1)[1].strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"\s*```$", "", cleaned).strip()

    start = cleaned.find("{")
    if start < 0:
        raise InferenceParseError("Model output did not contain a JSON object")

    depth = 0
    in_string = False
    escaped = False
    for index in range(start, len(cleaned)):
        char = cleaned[index]
        if escaped:
            escaped = False
        elif char == "\\" and in_string:
            escaped = True
        elif char == '"':
            in_string = not in_string
        elif not in_string and char == "{":
            depth += 1
        elif not in_string and char == "}":
            depth -= 1
            if depth == 0:
                candidate = cleaned[start : index + 1]
                try:
                    parsed = json.loads(candidate)
                except json.JSONDecodeError as exc:
                    raise InferenceParseError(
                        f"Model output contained invalid JSON: {exc.msg}"
                    ) from exc
                if not isinstance(parsed, dict):
                    raise InferenceParseError("Model output JSON must be an object")
                return parsed

    raise InferenceParseError("Model output contained an incomplete JSON object")
