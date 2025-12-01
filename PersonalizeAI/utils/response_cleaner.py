"""Utilities to extract and validate JSON responses from LLM text outputs.

This module provides helpers to:
- strip common fences (```),
- extract the first JSON object or array from free-form text,
- validate parsed JSON against simple Phase-3 schemas (generator, judge, rewrite).

The extraction routine is tolerant to quoted braces and simple escape sequences.
"""
from __future__ import annotations

import json
import logging
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger("PersonalizeAI.response_cleaner")


def _strip_fences(text: str) -> str:
    s = text.strip()
    if s.startswith("```"):
        # remove first fence line and last fence line if present
        lines = s.splitlines()
        if len(lines) >= 2 and lines[0].startswith("```"):
            # find last fence
            last_idx = None
            for i in range(len(lines) - 1, -1, -1):
                if lines[i].startswith("```"):
                    last_idx = i
                    break
            if last_idx is not None and last_idx > 0:
                return "\n".join(lines[1:last_idx])
            else:
                return "\n".join(lines[1:])
    return s


def _extract_json_at(text: str, start_idx: int) -> Optional[str]:
    """Extract a JSON substring starting at start_idx by bracket/brace balancing.

    This handles strings (quotes) and escaped characters so braces inside
    strings do not confuse bracket counting.
    Returns the JSON substring or None if matching end not found.
    """
    if start_idx >= len(text):
        return None
    opening = text[start_idx]
    if opening not in "[{":
        return None

    pairs = {"[": "]", "{": "}"}
    closing = pairs[opening]

    stack = [opening]
    in_string = False
    escape = False
    i = start_idx + 1
    while i < len(text):
        ch = text[i]
        if escape:
            escape = False
        elif ch == "\\":
            escape = True
        elif ch == '"':
            in_string = not in_string
        elif not in_string:
            if ch == opening:
                stack.append(ch)
            elif ch == closing:
                stack.pop()
                if not stack:
                    return text[start_idx : i + 1]
        i += 1

    return None


def extract_first_json(text: str) -> Any:
    """Find and parse the first JSON object/array in `text`.

    Raises ValueError on parse failure or if no JSON found.
    """
    if not isinstance(text, str):
        raise ValueError("Input must be a string")

    cleaned = _strip_fences(text)

    # find first brace or bracket
    for idx, ch in enumerate(cleaned):
        if ch in "[{":
            js = _extract_json_at(cleaned, idx)
            if js:
                try:
                    return json.loads(js)
                except Exception as exc:
                    logger.debug("Found JSON-like substring but failed to parse: %s", exc)
                    # try to be resilient: attempt to locate trailing characters that break parsing
                    raise ValueError(f"Failed to parse JSON: {exc}\nSubstring:\n{js}") from exc

    raise ValueError("No JSON object or array found in text")


def validate_generator_output(obj: Any) -> Tuple[bool, Optional[str]]:
    """Validate ai_message_generator output: list of variants with required keys.

    Returns (True, None) on success, else (False, error_message).
    """
    if not isinstance(obj, list):
        return False, "Expected a JSON array of variants"
    if len(obj) < 1:
        return False, "Expected at least one variant"

    for i, v in enumerate(obj):
        if not isinstance(v, dict):
            return False, f"Variant at index {i} is not an object"
        for key in ("id", "subject", "body", "cta"):
            if key not in v:
                return False, f"Variant at index {i} missing key '{key}'"
            if not isinstance(v[key], str):
                return False, f"Variant at index {i} key '{key}' must be a string"

    return True, None


def validate_judge_output(obj: Any) -> Tuple[bool, Optional[str]]:
    """Validate compliance judge output: object with is_compliant(bool) and reason (null|string)."""
    if not isinstance(obj, dict):
        return False, "Expected a JSON object"
    if "is_compliant" not in obj:
        return False, "Missing 'is_compliant' key"
    if not isinstance(obj["is_compliant"], bool):
        return False, "'is_compliant' must be boolean"
    if obj.get("reason") is not None and not isinstance(obj.get("reason"), str):
        return False, "'reason' must be null or a string"
    return True, None


def validate_rewrite_output(obj: Any) -> Tuple[bool, Optional[str]]:
    """Validate a single rewritten variant object.

    Expects dict with id, subject, body, cta strings.
    """
    if not isinstance(obj, dict):
        return False, "Expected a JSON object"
    for key in ("id", "subject", "body", "cta"):
        if key not in obj:
            return False, f"Missing '{key}' in rewrite output"
        if not isinstance(obj[key], str):
            return False, f"'{key}' must be a string"
    return True, None


def parse_and_validate_generator(text: str) -> List[Dict[str, Any]]:
    parsed = extract_first_json(text)
    ok, err = validate_generator_output(parsed)
    if not ok:
        raise ValueError(f"Invalid generator output: {err}")
    return parsed


def parse_and_validate_judge(text: str) -> Dict[str, Any]:
    parsed = extract_first_json(text)
    ok, err = validate_judge_output(parsed)
    if not ok:
        raise ValueError(f"Invalid judge output: {err}")
    return parsed


def parse_and_validate_rewrite(text: str) -> Dict[str, Any]:
    parsed = extract_first_json(text)
    ok, err = validate_rewrite_output(parsed)
    if not ok:
        raise ValueError(f"Invalid rewrite output: {err}")
    return parsed
