from __future__ import annotations

MAX_AI_CHAT_TURNS = 4
_MAX_QUESTION_CHARS = 2000
_MAX_ANSWER_CHARS = 3000


def normalize_history(raw: object) -> list[tuple[str, str]]:
    if not isinstance(raw, list):
        return []
    out: list[tuple[str, str]] = []
    for item in raw:
        if not isinstance(item, (list, tuple)) or len(item) != 2:
            continue
        q, a = str(item[0] or "").strip(), str(item[1] or "").strip()
        if q and a:
            out.append((q[:_MAX_QUESTION_CHARS], a[:_MAX_ANSWER_CHARS]))
    return out[-MAX_AI_CHAT_TURNS:]


def append_turn(history: list[tuple[str, str]], question: str, answer: str) -> list[tuple[str, str]]:
    rows = list(history)
    rows.append((question.strip()[:_MAX_QUESTION_CHARS], answer.strip()[:_MAX_ANSWER_CHARS]))
    return rows[-MAX_AI_CHAT_TURNS:]


def serialize_history(history: list[tuple[str, str]]) -> list[list[str]]:
    return [[q, a] for q, a in history]


def module_history_key(module_id: str, submodule_id: str | None) -> str:
    return f"mod_chat:{module_id}:{submodule_id or ''}"
