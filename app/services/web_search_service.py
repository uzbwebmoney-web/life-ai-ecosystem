from __future__ import annotations

import logging
import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)

_WEB_HINT_RE = re.compile(
    r"|".join(
        (
            r"telegram|телеграм|t\.me",
            r"канал|групп|channel|group|chat",
            r"ссылк|link|url|сайт|website|web\s*site",
            r"телефон|phone|контакт|contact|адрес|address|email|почт|e-mail",
            r"миграци|migration|агентств|agency|посольств|embassy",
            r"виз[ауы]?|visa|паспорт|passport",
            r"дай\s+(?:мне\s+)?(?:групп|канал|ссылк|контакт|телефон|номер|адрес)",
            r"где\s+(?:найти|взять|связаться|находится|записаться|оформить)",
            r"как\s+(?:связаться|найти|записаться|оформить|получить)",
            r"актуальн|сейчас|сегодня|текущ|latest|current|now|на\s+данный\s+момент",
            r"официальн|official|гос(?:услуг|орган)|government",
            r"расписани|schedule|график|часы\s+работ|working\s+hours",
            r"стоимость|цена|тариф|fee|price|сколько\s+стоит|how\s+much",
            r"курс\s+(?:валют|доллар|евро|usd|eur|rubl|рубл)",
            r"@[a-zA-Z0-9_]{3,}",
        )
    ),
    re.IGNORECASE,
)

_FORCE_WEB_RE = re.compile(
    r"|".join(
        (
            r"telegram|телеграм|t\.me|канал|групп|channel|group",
            r"дай\s+(?:мне\s+)?(?:групп|канал|ссылк|контакт|телефон|номер)",
            r"ссылк|link|url|сайт|website",
            r"контакт|contact|телефон|phone|адрес|address",
            r"@[a-zA-Z0-9_]{3,}",
        )
    ),
    re.IGNORECASE,
)

_MODULE_WEB_HINTS = frozenset(
    {
        "travel",
        "legal",
        "assistant",
        "ai_assistant",
        "business",
        "education",
        "home",
    }
)

_WEB_SEARCH_SYSTEM_NOTE = (
    "Если вопрос про контакты, Telegram-каналы/группы, сайты, адреса, правила, цены или "
    "актуальные сведения — используй веб-поиск. Указывай проверенные источники и ссылки. "
    "Если точных данных нет — скажи об этом честно, не выдумывай."
)


def should_use_web_search(user_message: str, *, module_id: str | None = None) -> tuple[bool, bool]:
    """Return (use_web_search, force_search)."""
    if not settings.web_search_enabled:
        return False, False
    text = (user_message or "").strip()
    if len(text) < 4:
        return False, False
    if _WEB_HINT_RE.search(text):
        return True, bool(_FORCE_WEB_RE.search(text))
    if module_id in _MODULE_WEB_HINTS and "?" in text:
        return True, False
    return False, False


def web_search_system_note() -> str:
    return _WEB_SEARCH_SYSTEM_NOTE


def _build_responses_input(
    user_content: str,
    chat_history: list[tuple[str, str]] | None,
) -> list[dict[str, str]] | str:
    if not chat_history:
        return user_content
    items: list[dict[str, str]] = []
    for past_q, past_a in chat_history:
        items.append({"role": "user", "content": past_q})
        items.append({"role": "assistant", "content": past_a})
    items.append({"role": "user", "content": user_content})
    return items


def _unwrap_ddg_url(href: str) -> str:
    if "duckduckgo.com/l/?" in href:
        parsed = urlparse(href)
        target = parse_qs(parsed.query).get("uddg", [""])[0]
        if target:
            return unquote(target)
    return href


async def fetch_ddg_context(query: str, *, max_results: int = 5) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (compatible; LifeAIBot/1.0)"},
            )
            resp.raise_for_status()
            html = resp.text
    except Exception as exc:
        logger.warning("DuckDuckGo search failed: %s", exc)
        return ""

    rows = re.findall(
        r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not rows:
        rows = re.findall(
            r'<a[^>]+rel="nofollow"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
            html,
            flags=re.IGNORECASE | re.DOTALL,
        )

    lines: list[str] = []
    for href, title, *rest in rows[:max_results]:
        snippet = unescape(re.sub(r"<[^>]+>", " ", rest[0] if rest else "")).strip()
        snippet = re.sub(r"\s+", " ", snippet)
        clean_title = unescape(re.sub(r"<[^>]+>", "", title)).strip()
        url = _unwrap_ddg_url(unescape(href))
        if not clean_title:
            continue
        block = f"• {clean_title}\n  {url}"
        if snippet:
            block += f"\n  {snippet[:280]}"
        lines.append(block)

    if not lines:
        return ""
    return "Актуальные результаты из интернета:\n" + "\n\n".join(lines)


async def call_ai_with_web_search(
    client,
    *,
    model: str,
    system: str,
    user_content: str,
    chat_history: list[tuple[str, str]] | None,
    max_output_tokens: int,
    force: bool,
    language: str,
):
    """OpenAI Responses API with web_search; returns (text, response)."""
    instructions = system + "\n\n" + _WEB_SEARCH_SYSTEM_NOTE
    payload = {
        "model": model,
        "instructions": instructions,
        "input": _build_responses_input(user_content, chat_history),
        "tools": [{"type": "web_search", "search_context_size": "medium"}],
        "tool_choice": "required" if force else "auto",
        "max_output_tokens": max_output_tokens,
    }
    response = await client.responses.create(**payload)
    text = (getattr(response, "output_text", None) or "").strip()
    return text, response


async def enrich_system_with_web_context(system: str, query: str, *, language: str) -> str:
    context = await fetch_ddg_context(query)
    if not context:
        return system
    return system + "\n\n" + context + "\n\nИспользуй эти данные, если они релевантны запросу."
