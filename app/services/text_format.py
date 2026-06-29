from __future__ import annotations

import html
import re

_MD_BOLD_RE = re.compile(r"\*\*(.+?)\*\*", re.DOTALL)
_HTTP_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)
_TME_PLAIN_RE = re.compile(r"(?<![/\w@])(?:t\.me|telegram\.me)/([a-zA-Z0-9_+]{3,})", re.IGNORECASE)


def format_ai_reply(text: str) -> str:
    """Strip markdown bold markers; bot uses Telegram HTML, not markdown."""
    cleaned = _MD_BOLD_RE.sub(r"\1", text)
    return cleaned.replace("**", "").replace("__", "")


def _linkify_plain_text(plain: str) -> str:
    """Escape HTML but keep http(s) and t.me URLs clickable in Telegram."""
    if not plain:
        return ""
    spans: list[tuple[int, int, str]] = []
    for match in _HTTP_URL_RE.finditer(plain):
        url = match.group(0).rstrip(".,;:!?)\"'")
        safe_url = html.escape(url, quote=True)
        spans.append((match.start(), match.end(), f'<a href="{safe_url}">{html.escape(url, quote=False)}</a>'))
    for match in _TME_PLAIN_RE.finditer(plain):
        if any(start <= match.start() < end for start, end, _ in spans):
            continue
        handle = match.group(1)
        url = f"https://t.me/{handle}"
        safe_url = html.escape(url, quote=True)
        label = html.escape(match.group(0), quote=False)
        spans.append((match.start(), match.end(), f'<a href="{safe_url}">{label}</a>'))
    if not spans:
        return html.escape(plain, quote=False)
    spans.sort(key=lambda item: item[0])
    parts: list[str] = []
    last = 0
    for start, end, chunk in spans:
        if start > last:
            parts.append(html.escape(plain[last:start], quote=False))
        parts.append(chunk)
        last = end
    if last < len(plain):
        parts.append(html.escape(plain[last:], quote=False))
    return "".join(parts)


def format_ai_reply_html(text: str) -> str:
    """Escape HTML but keep URLs clickable in Telegram."""
    plain = format_ai_reply(text)
    return _linkify_plain_text(plain) or html.escape(plain, quote=False)


def escape_telegram_html(text: str) -> str:
    return html.escape(text or "", quote=False)
