from __future__ import annotations

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
        "health",
        "car",
        "finance",
        "nutrition",
        "organizer",
        "vault",
        "music",
        "shopping",
        "generic",
    }
)

_WEB_SEARCH_INSTRUCTIONS: dict[str, str] = {
    "ru": (
        "Веб-поиск доступен во всех разделах бота. Используй его, когда нужны актуальные данные: "
        "контакты, Telegram, сайты, цены, адреса, правила, законы, расписания, новости, "
        "инструкции по услугам и организациям. "
        "В ответе указывай полные ссылки (https://…, t.me/…). "
        "Не давай только названия без ссылок, если ссылки найдены. "
        "Для общих знаний без необходимости свежих данных можно ответить без поиска."
    ),
    "uz": (
        "Veb-qidiruv botning barcha bo'limlarida mavjud. Aktual ma'lumot kerak bo'lsa foydalaning: "
        "kontaktlar, Telegram, saytlar, narxlar, manzillar, qoidalar, qonunlar, jadval, yangiliklar. "
        "Javobda to'liq havolalarni (https://…, t.me/…) yozing. "
        "Havolalar topilsa, faqat nom berish taqiqlanadi. "
        "Umumiy bilim uchun qidiruv shart emas."
    ),
    "en": (
        "Web search is available in every bot section. Use it when fresh data is needed: "
        "contacts, Telegram, websites, prices, addresses, rules, laws, schedules, news. "
        "Include full links (https://…, t.me/…) in answers. "
        "Do not give names only when links were found. "
        "For general knowledge without fresh data, search is optional."
    ),
}


def should_use_web_search(user_message: str, *, module_id: str | None = None) -> tuple[bool, bool]:
    if not settings.web_search_enabled:
        return False, False
    text = (user_message or "").strip()
    if len(text) < 4:
        return False, False

    force = bool(_FORCE_WEB_RE.search(text))
    if _WEB_HINT_RE.search(text):
        return True, force

    if settings.web_search_all_modules:
        if module_id is not None:
            return True, force
        words = text.split()
        if "?" in text or len(words) >= 4:
            return True, False

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
    title = {
        "ru": "🔗 Ссылки",
        "uz": "🔗 Havolalar",
        "en": "🔗 Links",
    }.get(lang, "🔗 Ссылки")
    lines = "\n".join(f"• {link}" for link in extra[:12])
    return f"{answer.rstrip()}\n\n{title}:\n{lines}"


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


async def fetch_web_context(
    user_message: str,
    *,
    language: str = "ru",
    country: str | None = None,
    max_results: int = 6,
) -> tuple[str, list[str]]:
    queries = build_search_queries(user_message, language=language, country=country)
    if not queries:
        return "", []

    seen_urls: set[str] = set()
    lines: list[str] = []
    all_links: list[str] = []

    for query in queries:
        for title, url, snippet in await _ddg_search_once(query, max_results=max_results):
            if url in seen_urls:
                continue
            seen_urls.add(url)
            block = f"• {title}\n  {url}"
            if snippet:
                block += f"\n  {snippet[:280]}"
            lines.append(block)
            chunk_text = f"{url} {snippet} {title}"
            for link in collect_links_from_text(chunk_text):
                if link not in all_links:
                    all_links.append(link)
            if len(lines) >= max_results:
                break
        if len(lines) >= max_results:
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
        parts.append(tme_header + ":\n" + "\n".join(f"• {link}" for link in show[:10]))
    if lines:
        parts.append("\n\n".join(lines))
    return "\n\n".join(parts), all_links


async def fetch_ddg_context(query: str, *, max_results: int = 5) -> str:
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
    links = merge_unique_links(web_links or [], collect_links_from_text(text))
    text = append_links_footer(text, links, language=language)
    return text, response


async def enrich_system_with_web_context(
    system: str,
    query: str,
    *,
    language: str,
    country: str | None = None,
) -> str:
    context, _ = await fetch_web_context(query, language=language, country=country)
    if not context:
        return system + "\n\n" + web_search_system_note(language)
    use_note = {
        "ru": "Используй эти данные в ответе. Укажи полные URL, особенно t.me.",
        "uz": "Bu ma'lumotlardan foydalaning. To'liq URL yozing, ayniqsa t.me.",
        "en": "Use this data in your answer. Include full URLs, especially t.me.",
    }.get(normalize_lang(language), "Используй эти данные в ответе.")
    return system + "\n\n" + context + "\n\n" + use_note + "\n\n" + web_search_system_note(language)
