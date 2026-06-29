from __future__ import annotations

import html
import re

_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)


def format_ai_reply(text: str) -> str:
    """Strip markdown bold markers; bot uses Telegram HTML, not markdown."""
    cleaned = _MD_BOLD_RE.sub(r"\1", text)
    return cleaned.replace("**", "").replace("__", "")


def format_ai_reply_html(text: str) -> str:
    """Escape HTML but keep URLs clickable in Telegram."""
    plain = format_ai_reply(text)
    if not plain:
        return ""
    parts: list[str] = []
    last = 0
    for match in _HTTP_URL_RE.finditer(plain):
        if match.start() > last:
            parts.append(html.escape(plain[last : match.start()], quote=False))
        url = match.group(0).rstrip(".,;:!?)\"'")
        safe_url = html.escape(url, quote=True)
        parts.append(f'<a href="{safe_url}">{html.escape(url, quote=False)}</a>')
        last = match.end()
    if last < len(plain):
        parts.append(html.escape(plain[last:], quote=False))
    return "".join(parts) or html.escape(plain, quote=False)


_HTTP_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)


def escape_telegram_html(text: str) -> str:
    return html.escape(text or "", quote=False)