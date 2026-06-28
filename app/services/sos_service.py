from __future__ import annotations

from app.core.i18n import t


SOS_TOPICS: tuple[str, ...] = (
    "first_aid",
    "phones",
    "accident",
    "passport",
    "poison",
    "burn",
)


def sos_menu_text(lang: str) -> str:
    return t(lang, "sos_menu")


def sos_topic_text(lang: str, topic: str) -> str:
    key = f"sos_{topic}"
    return t(lang, key)
