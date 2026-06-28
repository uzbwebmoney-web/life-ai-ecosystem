from __future__ import annotations

import re

_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)


def format_ai_reply(text: str) -> str:
    """Strip markdown bold markers; bot uses Telegram HTML, not markdown."""
    cleaned = _MD_BOLD_RE.sub(r"\1", text)
    return cleaned.replace("**", "").replace("__", "")
