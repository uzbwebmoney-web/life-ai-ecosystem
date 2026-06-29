from __future__ import annotations

import logging
import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from app.core.config import settings
from app.core.i18n import normalize_lang

logger = logging.getLogger(__name__)

_TME_RE = re.compile(r"https?://(?:t\.me|telegram\.me)/[^\s<>\"']+", re.IGNORECASE)

_WEB_HINT_RE = re.compile(
    r"|".join(
        (
            r"telegram|телеграм|t\.me",
            r"канал|групп|channel|group|chat|guruh|grupp",
            r"ссылк|link|url|сайт|website|web\s*site|havola",
            r"телефон|phone|контакт|contact|адрес|address|email|почт|e-mail|aloqa|manzil|telefon",
            r"миграци|migration|migratsiya|immigr|агентств|agency|agentlik|посольств|embassy|elchixona",
            r"виз[ауы]?|visa|viza|паспорт|passport|pasport",
            r"дай\s+(?:мне\s+)?(?:групп|канал|ссылк|контакт|телефон|номер|адрес)",
            r"(?:ber|bering|boring|top)(?:ing|ish|)?",
            r"где\s+(?:найти|взять|связаться|находится|записаться|оформить)",
            r"qayerda|qanday\s+top",
            r"как\s+(?:связаться|найти|записаться|оформить|получить)",
            r"актуальн|сейчас|сегодня|текущ|latest|current|now|на\s+данный\s+момент|hozir|bugun",
            r"официальн|official|гос(?:услуг|organ)|government|rasmiy",
            r"расписани|schedule|график|часы\s+работ|working\s+hours|ish\s+vaqti",
            r"стоимость|цена|тариф|fee|price|сколько\s+стоит|how\s+much|narxi|qancha",
            r"курс\s+(?:валют|доллар|евро|usd|eur|rubl|рубл)",
            r"@[a-zA-Z0-9_]{3,}",
        )
    ),
    re.IGNORECASE,
)

_FORCE_WEB_RE = re.compile(
    r"|".join(
        (
            r"telegram|телеграм|t\.me|канал|групп|channel|group|guruh|grupp",
            r"дай\s+(?:мне\s+)?(?:групп|канал|ссылк|контакт|телефон|номер)",
            r"(?:havola|link|url|ссылк|сайт|website)",
            r"контакт|contact|aloqa|телефон|phone|telefon|адрес|address|manzil",
            r"ber(?:ing|ish|)?|boring",
            r"@[a-zA-Z0-9_]{3,}",
            r"(?:migratsiya|migration|миграци).{0,40}(?:telegram|guruh|kanal|havola)",
            r"(?:telegram|guruh|kanal|havola).{0,40}(?:migratsiya|migration|миграци)",
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

_WEB_SEARCH_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "Если пользователь просит Telegram-канал/группу, сайт, телефон или контакты — "
        "обязательно используй веб-поиск и блок «Актуальные результаты из интернета». "
        "Давай конкретные ссылки (особенно t.me/…), если они есть в результатах. "
        "Запрещено отвечать общими советами «откройте Telegram и ищите сами», если поиск уже дал ссылки. "
        "Если ссылок нет — честно скажи, что не нашёл, и предложи официальные сайты."
    ),
    "uz": (
        "Foydalanuvchi Telegram kanal/guruh, sayt, telefon yoki kontaktlarni so'rasa — "
        "albatta veb-qidiruv va «Aktual internet natijalari» blokidan foydalaning. "
        "Aniq havolalarni (ayniqsa t.me/…) bering, agar natijalarda bo'lsa. "
        "«Telegramni oching va o'zingiz qidiring» kabi umumiy maslahat berish taqiqlanadi, "
        "agar qidiruvda havolalar topilgan bo'lsa. Topilmasa — topilmadi deb ayting."
    ),
    "en": (
        "If the user asks for a Telegram channel/group, website, phone, or contacts — "
        "you must use web search and the «Current web results» block. "
        "Provide concrete links (especially t.me/…) when present in results. "
        "Do not reply with generic advice like «open Telegram and search yourself» when links were found. "
        "If nothing was found, say so honestly."
    ),
}


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


def web_search_system_note(language: str = "ru") -> str:
    lang = normalize_lang(language)
    return _WEB_SEARCH_INSTRUCTIONS.get(lang, _WEB_SEARCH_INSTRUCTIONS["ru"])


def build_search_queries(
    user_message: str,
    *,
    language: str = "ru",
    country: str | None = None,
) -> list[str]:
    base = re.sub(r"\s+", " ", (user_message or "").strip())
    if not base:
        return []
    country = (country or settings.default_passport_country or "").strip()
    queries = [base]
    lower = base.lower()

    if "telegram" not in lower and "t.me" not in lower:
        queries.append(f"{base} telegram t.me")
    if country and country.lower() not in lower:
        queries.append(f"{base} {country}")

    if re.search(r"migratsiya|migration|миграци", lower, re.IGNORECASE):
        if country:
            queries.append(f"{country} migratsiya agentligi rasmiy telegram t.me")
            queries.append(f"migration agency {country} official telegram channel")

    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            unique.append(q[:200])
    return unique[:4]


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


def _parse_ddg_html(html: str, *, max_results: int) -> list[tuple[str, str, str]]:
    rows = re.findall(
        r'<a[^>]+class="result-link"[^>]+href="([^"]+)"[^>]*>(.*?)</a>.*?'
        r'<td[^>]*class="result-snippet"[^>]*>(.*?)</td>',
        html,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not rows:
        rows = [
            (href, title, "")
            for href, title in re.findall(
                r'<a[^>]+rel="nofollow"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
                html,
                flags=re.IGNORECASE | re.DOTALL,
            )
        ]

    parsed: list[tuple[str, str, str]] = []
    for href, title, snippet in rows[: max_results * 2]:
        clean_title = unescape(re.sub(r"<[^>]+>", "", title)).strip()
        clean_snippet = unescape(re.sub(r"<[^>]+>", " ", snippet)).strip()
        clean_snippet = re.sub(r"\s+", " ", clean_snippet)
        url = _unwrap_ddg_url(unescape(href))
        if clean_title:
            parsed.append((clean_title, url, clean_snippet))
    return parsed[:max_results]


async def _ddg_search_once(query: str, *, max_results: int = 5) -> list[tuple[str, str, str]]:
    try:
        async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as client:
            resp = await client.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": query},
                headers={"User-Agent": "Mozilla/5.0 (compatible; LifeAIBot/1.0)"},
            )
            resp.raise_for_status()
            return _parse_ddg_html(resp.text, max_results=max_results)
    except Exception as exc:
        logger.warning("DuckDuckGo search failed for %r: %s", query[:80], exc)
        return []


async def fetch_ddg_context(query: str, *, max_results: int = 5) -> str:
    return await fetch_web_context(query, language="ru", max_results=max_results)


async def fetch_web_context(
    user_message: str,
    *,
    language: str = "ru",
    country: str | None = None,
    max_results: int = 6,
) -> str:
    queries = build_search_queries(user_message, language=language, country=country)
    if not queries:
        return ""

    seen_urls: set[str] = set()
    lines: list[str] = []
    tme_links: list[str] = []

    for query in queries:
        for title, url, snippet in await _ddg_search_once(query, max_results=max_results):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            block = f"• {title}\n  {url}"
            if snippet:
                block += f"\n  {snippet[:280]}"
            lines.append(block)
            for match in _TME_RE.findall(f"{url} {snippet} {title}"):
                if match not in tme_links:
                    tme_links.append(match)
            if len(lines) >= max_results:
                break
        if len(lines) >= max_results:
            break

    if not lines and not tme_links:
        return ""

    lang = normalize_lang(language)
    header = {
        "ru": "Актуальные результаты из интернета",
        "uz": "Aktual internet natijalari",
        "en": "Current web results",
    }.get(lang, "Актуальные результаты из интернета")

    parts = [header + ":"]
    if tme_links:
        tme_header = {
            "ru": "Telegram-ссылки (t.me)",
            "uz": "Telegram havolalar (t.me)",
            "en": "Telegram links (t.me)",
        }.get(lang, "Telegram-ссылки (t.me)")
        parts.append(tme_header + ":\n" + "\n".join(f"• {link}" for link in tme_links[:8]))
    if lines:
        parts.append("\n\n".join(lines))
    return "\n\n".join(parts)


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
    country: str | None = None,
):
    """OpenAI Responses API with web_search; returns (text, response)."""
    web_context = await fetch_web_context(
        user_content,
        language=language,
        country=country,
        max_results=8,
    )
    note = web_search_system_note(language)
    instructions = system + "\n\n" + note
    if web_context:
        instructions += "\n\n" + web_context

    payload = {
        "model": model,
        "instructions": instructions,
        "input": _build_responses_input(user_content, chat_history),
        "tools": [{"type": "web_search", "search_context_size": "high"}],
        "tool_choice": "required" if force else "auto",
        "max_output_tokens": max_output_tokens,
    }
    response = await client.responses.create(**payload)
    text = (getattr(response, "output_text", None) or "").strip()
    return text, response


async def enrich_system_with_web_context(
    system: str,
    query: str,
    *,
    language: str,
    country: str | None = None,
) -> str:
    context = await fetch_web_context(query, language=language, country=country)
    if not context:
        return system + "\n\n" + web_search_system_note(language)
    use_note = {
        "ru": "Используй эти данные в ответе. Если есть t.me — обязательно укажи их пользователю.",
        "uz": "Bu ma'lumotlardan foydalaning. t.me havolalar bo'lsa — foydalanuvchiga yozing.",
        "en": "Use this data in your answer. If t.me links exist — include them for the user.",
    }.get(normalize_lang(language), "Используй эти данные в ответе.")
    return system + "\n\n" + context + "\n\n" + use_note + "\n\n" + web_search_system_note(language)
