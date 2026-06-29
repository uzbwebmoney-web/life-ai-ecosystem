from __future__ import annotations

import asyncio
import logging
import re
from html import unescape
from urllib.parse import parse_qs, unquote, urlparse

import httpx

from app.core.config import settings
from app.core.i18n import normalize_lang

logger = logging.getLogger(__name__)

_TME_BARE_RE = re.compile(r"(?<![/\w@])(?:t\.me|telegram\.me)/([a-zA-Z0-9_+]{3,})", re.IGNORECASE)
_TG_HANDLE_RE = re.compile(r"(?<![/\w])@([a-zA-Z][a-zA-Z0-9_]{3,})")
_HTTP_URL_RE = re.compile(r"https?://[^\s<>\"']+", re.IGNORECASE)

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

_WEB_SEARCH_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "Веб-поиск включён для каждого запроса. Сначала ищи актуальную информацию в интернете, "
        "затем отвечай по сути. Используй найденные данные о контактах, ценах, адресах, правилах, "
        "законах, расписаниях, Telegram-каналах и официальных сайтах. "
        "В ответе обязательно указывай полные ссылки (https://…, t.me/…). "
        "Не используй markdown-ссылки вида [текст](url) — только голые URL или «название: https://…». "
        "Не давай только названия без ссылок, если ссылки найдены."
    ),
    "uz": (
        "Har bir so'rovda veb-qidiruv yoqilgan. Avval internetdan aktual ma'lumot qidiring, "
        "keyin javob bering. Kontaktlar, narxlar, manzillar, qoidalar, Telegram va rasmiy saytlar "
        "uchun topilgan ma'lumotlardan foydalaning. "
        "Javobda to'liq havolalarni (https://…, t.me/…) yozing. "
        "Markdown [matn](url) ishlatmang — faqat to'g'ridan-to'g'ri URL."
    ),
    "en": (
        "Web search is enabled for every request. Search the web first for fresh data, then answer. "
        "Use found contacts, prices, addresses, rules, Telegram channels, and official sites. "
        "Always include full links (https://…, t.me/…) in the answer. "
        "Never use markdown links [text](url) — plain URLs only."
    ),
}

_USE_NOTE: dict[str, str] = {
    "ru": "Используй блок «Актуальные результаты из интернета» и результаты OpenAI web search. Укажи полные URL.",
    "uz": "«Aktual internet natijalari» va OpenAI qidiruv natijalaridan foydalaning. To'liq URL yozing.",
    "en": "Use the «Current web results» block and OpenAI web search results. Include full URLs.",
}


def should_use_web_search(user_message: str, *, module_id: str | None = None) -> tuple[bool, bool]:
    if not settings.web_search_enabled:
        return False, False
    text = (user_message or "").strip()
    if len(text) < 3:
        return False, False
    force_match = bool(_FORCE_WEB_RE.search(text))
    if settings.web_search_all_modules:
        force = settings.web_search_force_required or force_match
        return True, force
    if force_match:
        return True, True
    return False, False


def web_search_system_note(language: str = "ru") -> str:
    lang = normalize_lang(language)
    return _WEB_SEARCH_INSTRUCTIONS.get(lang, _WEB_SEARCH_INSTRUCTIONS["ru"])


def _web_search_tool() -> dict:
    tool: dict = {
        "type": "web_search",
        "search_context_size": settings.web_search_context_size,
    }
    if settings.web_search_unlimited_context:
        tool["return_token_budget"] = "unlimited"
    return tool


def build_search_queries(
    user_message: str,
    *,
    language: str = "ru",
    country: str | None = None,
    module_id: str | None = None,
) -> list[str]:
    base = re.sub(r"\s+", " ", (user_message or "").strip())
    if not base:
        return []
    country = (country or settings.default_passport_country or "").strip()
    queries = [base]
    lower = base.lower()

    if country and country.lower() not in lower:
        queries.append(f"{base} {country}")
    if module_id:
        queries.append(f"{base} {module_id.replace('_', ' ')}")
    if "telegram" not in lower and "t.me" not in lower:
        queries.append(f"{base} telegram t.me")
    if re.search(r"migratsiya|migration|миграци", lower, re.IGNORECASE) and country:
        queries.append(f"{country} migratsiya agentligi rasmiy telegram t.me")
        queries.append(f"migration agency {country} official telegram")

    seen: set[str] = set()
    unique: list[str] = []
    for q in queries:
        key = q.lower()
        if key not in seen:
            seen.add(key)
            unique.append(q[:240])
    return unique[: settings.web_search_max_queries]


def collect_links_from_text(text: str) -> list[str]:
    if not text:
        return []
    found: list[str] = []
    seen: set[str] = set()

    def _add(url: str) -> None:
        clean = url.rstrip(".,;:!?)\"'")
        key = clean.lower().rstrip("/")
        if clean and key not in seen:
            seen.add(key)
            found.append(clean)

    for url in _HTTP_URL_RE.findall(text):
        _add(url)
    for match in _TME_BARE_RE.finditer(text):
        _add(f"https://t.me/{match.group(1)}")
    for handle in _TG_HANDLE_RE.findall(text):
        _add(f"https://t.me/{handle}")
    return found


def merge_unique_links(*groups: list[str]) -> list[str]:
    seen: set[str] = set()
    merged: list[str] = []
    for group in groups:
        for link in group:
            key = link.lower().rstrip("/")
            if key not in seen:
                seen.add(key)
                merged.append(link)
    return merged


def append_links_footer(answer: str, links: list[str], *, language: str = "ru") -> str:
    if not links:
        return answer
    existing = {u.lower().rstrip("/") for u in collect_links_from_text(answer)}
    extra = [link for link in links if link.lower().rstrip("/") not in existing]
    if not extra:
        return answer
    lang = normalize_lang(language)
    title = {"ru": "🔗 Ссылки", "uz": "🔗 Havolalar", "en": "🔗 Links"}.get(lang, "🔗 Ссылки")
    limit = settings.web_search_max_links_footer
    lines = "\n".join(f"• {_link_label(link)}\n  {link}" for link in extra[:limit])
    return f"{answer.rstrip()}\n\n{title}:\n{lines}"


def _link_label(url: str) -> str:
    try:
        from urllib.parse import urlparse

        host = urlparse(url).netloc.replace("www.", "")
        return host or url[:60]
    except Exception:
        return url[:60]


def merge_system_with_web_context(
    system: str,
    web_context: str,
    *,
    language: str = "ru",
) -> str:
    if not web_context.strip():
        return system + "\n\n" + web_search_system_note(language)
    lang = normalize_lang(language)
    note = _USE_NOTE.get(lang, _USE_NOTE["ru"])
    return system + "\n\n" + web_context + "\n\n" + note + "\n\n" + web_search_system_note(language)


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
    if not rows:
        rows = [
            (href, title, "")
            for href, title in re.findall(
                r'class="result__a"[^>]+href="([^"]+)"[^>]*>(.*?)</a>',
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
        if clean_title and not url.startswith("//duckduckgo.com"):
            parsed.append((clean_title, url, clean_snippet))
    return parsed[:max_results]


async def _ddg_search_once(query: str, *, max_results: int = 8) -> list[tuple[str, str, str]]:
    headers = {"User-Agent": "Mozilla/5.0 (compatible; LifeAIBot/1.0)"}
    timeout = httpx.Timeout(settings.web_search_timeout_seconds)
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.post(
                "https://lite.duckduckgo.com/lite/",
                data={"q": query},
                headers=headers,
            )
            resp.raise_for_status()
            parsed = _parse_ddg_html(resp.text, max_results=max_results)
            if parsed:
                return parsed
            resp2 = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": query},
                headers=headers,
            )
            resp2.raise_for_status()
            return _parse_ddg_html(resp2.text, max_results=max_results)
    except Exception as exc:
        logger.warning("DuckDuckGo search failed for %r: %s", query[:80], exc)
        return []


async def fetch_web_context(
    user_message: str,
    *,
    language: str = "ru",
    country: str | None = None,
    module_id: str | None = None,
    max_results: int | None = None,
) -> tuple[str, list[str]]:
    limit = max_results or settings.web_search_max_results
    per_query = max(4, limit // max(1, settings.web_search_max_queries // 2))
    queries = build_search_queries(
        user_message,
        language=language,
        country=country,
        module_id=module_id,
    )
    if not queries:
        return "", []

    search_tasks = [_ddg_search_once(q, max_results=per_query) for q in queries]
    batches = await asyncio.gather(*search_tasks)

    seen_urls: set[str] = set()
    lines: list[str] = []
    all_links: list[str] = []

    for batch in batches:
        for title, url, snippet in batch:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            block = f"• {title}\n  {url}"
            if snippet:
                block += f"\n  {snippet[:400]}"
            lines.append(block)
            chunk_text = f"{url} {snippet} {title}"
            for link in collect_links_from_text(chunk_text):
                if link not in all_links:
                    all_links.append(link)
            if len(lines) >= limit:
                break
        if len(lines) >= limit:
            break

    if not lines and not all_links:
        return "", []

    lang = normalize_lang(language)
    header = {
        "ru": "Актуальные результаты из интернета",
        "uz": "Aktual internet natijalari",
        "en": "Current web results",
    }.get(lang, "Актуальные результаты из интернета")

    parts = [header + ":"]
    if all_links:
        tme_header = {
            "ru": "Telegram-ссылки (t.me)",
            "uz": "Telegram havolalar (t.me)",
            "en": "Telegram links (t.me)",
        }.get(lang, "Telegram-ссылки (t.me)")
        tme_only = [l for l in all_links if "t.me/" in l.lower() or "telegram.me/" in l.lower()]
        show = tme_only or all_links
        parts.append(tme_header + ":\n" + "\n".join(f"• {link}" for link in show[:15]))
    if lines:
        parts.append("\n\n".join(lines))
    return "\n\n".join(parts), all_links


async def fetch_ddg_context(query: str, *, max_results: int = 8) -> str:
    context, _ = await fetch_web_context(query, language="ru", max_results=max_results)
    return context


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
    web_context: str = "",
    web_links: list[str] | None = None,
):
    instructions = merge_system_with_web_context(system, web_context, language=language)
    tool_choice = "required" if force else "auto"
    payload = {
        "model": model,
        "instructions": instructions,
        "input": _build_responses_input(user_content, chat_history),
        "tools": [_web_search_tool()],
        "tool_choice": tool_choice,
        "max_output_tokens": max_output_tokens,
    }

    text = ""
    response = None
    try:
        response = await client.responses.create(**payload)
        text = (getattr(response, "output_text", None) or "").strip()
    except Exception as exc:
        if "return_token_budget" in str(exc).lower() or "unknown" in str(exc).lower():
            logger.warning("Web search with unlimited context failed, retrying: %s", exc)
            payload["tools"] = [{"type": "web_search", "search_context_size": settings.web_search_context_size}]
            response = await client.responses.create(**payload)
            text = (getattr(response, "output_text", None) or "").strip()
        else:
            raise

    links = merge_unique_links(web_links or [], collect_links_from_text(text), collect_links_from_text(web_context))
    if text:
        text = append_links_footer(text, links, language=language)
    return text, response


async def enrich_system_with_web_context(
    system: str,
    query: str,
    *,
    language: str,
    country: str | None = None,
    module_id: str | None = None,
    web_context: str | None = None,
) -> str:
    context = web_context
    if not context:
        context, _ = await fetch_web_context(
            query,
            language=language,
            country=country,
            module_id=module_id,
        )
    return merge_system_with_web_context(system, context or "", language=language)
