"""Reusable prompt fragments for orchestrated agents (Phase 17)."""

from __future__ import annotations

import json
from typing import Any

JSON_OUTPUT_RULES = """
Return ONLY valid JSON matching the schema described. No markdown fences.
Use double quotes for all keys and string values.
If a field is unknown, use null, empty string, or empty array as appropriate.
"""

RECRUITER_TONE = """
Write as an experienced technical recruiter and interview coach.
Be specific, actionable, and professional. Avoid generic praise.
Reference evidence from the candidate's answers when possible.
"""


def build_structured_user_block(title: str, data: dict[str, Any], *, max_chars: int = 12000) -> str:
    serialized = json.dumps(data, indent=2, default=str)
    if len(serialized) > max_chars:
        serialized = serialized[:max_chars] + "\n…(truncated)"
    return f"### {title}\n{serialized}\n"
