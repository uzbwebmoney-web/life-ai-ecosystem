from __future__ import annotations

import json
import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import LifeRecord
from app.services.life_data import add_record

VAULT_MODULE = "vault"
VAULT_SUBMODULES = ("documents", "passport", "policies", "warranty", "receipts", "notes")
VAULT_FILE_SUBMODULES = VAULT_SUBMODULES

VAULT_FOLDER_BY_SUBMODULE: dict[str, str] = {
    "documents": "contracts",
    "passport": "passport",
    "policies": "contracts",
    "warranty": "warranty",
    "receipts": "receipts",
    "notes": "photos",
}

VAULT_SEARCH_KEYWORDS: dict[str, str] = {
    "documents": "documents hujjatlar документы договор contract shartnoma",
    "passport": "passport pasport паспорт",
    "policies": "policies polis полис insurance sug'urta страховка",
    "warranty": "warranty kafolat гарантия talon",
    "receipts": "receipts chek чек касса check",
    "notes": "notes qayd заметка запись note",
}

def vault_folder_for_submodule(submodule_id: str) -> str:
    return VAULT_FOLDER_BY_SUBMODULE.get(submodule_id, "contracts")


def vault_search_tags(submodule_id: str) -> str:
    return VAULT_SEARCH_KEYWORDS.get(submodule_id, submodule_id)


def vault_file_title(submodule_id: str, lang: str, *, filename: str = "") -> str:
    from app.core.i18n import t

    if filename:
        return filename[:200]
    labels = {
        "documents": ("Документ", "Hujjat", "Document"),
        "passport": ("Паспорт", "Pasport", "Passport"),
        "policies": ("Полис", "Polis", "Policy"),
        "warranty": ("Гарантия", "Kafolat", "Warranty"),
        "receipts": ("Чек", "Chek", "Receipt"),
        "notes": ("Заметка", "Qayd", "Note"),
    }
    idx = {"ru": 0, "uz": 1, "en": 2}.get(lang, 0)
    label = labels.get(submodule_id, ("Файл", "Fayl", "File"))[idx]
    return f"{label} — {t(lang, 'photo_title_default')}"


def vault_file_meta(
    submodule_id: str,
    file_id: str,
    *,
    mime: str | None = None,
    folder: str | None = None,
    kind: str | None = None,
) -> str:
    if kind is None:
        kind = "document" if mime and not mime.startswith("image/") else "photo"
    payload: dict[str, str] = {
        "telegram_file_id": file_id,
        "file_kind": kind,
        "archive_folder": folder or vault_folder_for_submodule(submodule_id),
    }
    if mime:
        payload["mime"] = mime
    return json.dumps(payload, ensure_ascii=False)


SUBMODULE_ICONS: dict[str, str] = {
    "documents": "📄",
    "passport": "🛂",
    "policies": "📋",
    "warranty": "🧾",
    "receipts": "🧾",
    "notes": "📝",
}


async def add_vault_item(
    session: AsyncSession,
    *,
    user_id: int,
    submodule_id: str,
    title: str,
    body: str = "",
    amount: float | None = None,
    profile_id: int | None = None,
    meta_json: str | None = None,
) -> LifeRecord:
    tagged_body = body.strip()
    tags = vault_search_tags(submodule_id)
    if tagged_body and not tagged_body.startswith(tags):
        tagged_body = f"{tags}\n{tagged_body}"
    elif not tagged_body:
        tagged_body = tags
    return await add_record(
        session,
        user_id=user_id,
        module_id=VAULT_MODULE,
        submodule_id=submodule_id,
        title=title.strip()[:255],
        body=tagged_body[:4000],
        amount=amount,
        currency="UZS" if amount else None,
        profile_id=profile_id,
        meta_json=meta_json,
    )


async def attach_file_to_record(
    session: AsyncSession,
    record: LifeRecord,
    *,
    file_id: str,
    mime: str | None = None,
    kind: str | None = None,
) -> LifeRecord:
    record.meta_json = vault_file_meta(
        record.submodule_id,
        file_id,
        mime=mime,
        kind=kind,
    )
    await session.commit()
    await session.refresh(record)
    return record


async def list_vault_items(
    session: AsyncSession,
    user_id: int,
    submodule_id: str,
    *,
    limit: int = 50,
) -> list[LifeRecord]:
    rows = (
        await session.execute(
            select(LifeRecord)
            .where(
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == VAULT_MODULE,
                LifeRecord.submodule_id == submodule_id,
            )
            .order_by(LifeRecord.created_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def get_vault_item(session: AsyncSession, user_id: int, record_id: int) -> LifeRecord | None:
    return (
        await session.execute(
            select(LifeRecord).where(
                LifeRecord.id == record_id,
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == VAULT_MODULE,
            )
        )
    ).scalar_one_or_none()


def parse_stored_file(record: LifeRecord) -> tuple[str, str | None, str] | None:
    raw_meta = record.meta_json or ""
    if raw_meta:
        try:
            data = json.loads(raw_meta)
            file_id = data.get("telegram_file_id")
            if file_id:
                return (
                    str(file_id),
                    data.get("mime") or None,
                    str(data.get("file_kind") or "photo"),
                )
        except (json.JSONDecodeError, TypeError):
            pass
    match = re.search(r"file_id=([^\s\n]+)", record.body or "")
    if not match:
        return None
    mime_match = re.search(r"mime=([^\s\n]+)", record.body or "")
    mime = mime_match.group(1) if mime_match else None
    kind = "document" if mime and not mime.startswith("image/") else "photo"
    return match.group(1), mime, kind


def record_has_file(record: LifeRecord) -> bool:
    return parse_stored_file(record) is not None


def vault_text_body(record: LifeRecord) -> str:
    body = (record.body or "").strip()
    if not body:
        return ""
    if "file_id=" not in body:
        lines = body.splitlines()
        tags = vault_search_tags(record.submodule_id)
        if lines and lines[0].strip() == tags:
            lines = lines[1:]
        return "\n".join(lines).strip()
    parts = body.split("\n\n", 1)
    return parts[1].strip() if len(parts) > 1 else ""


def format_vault_text_view(record: LifeRecord, lang: str) -> str:
    from app.core.i18n import t

    lines = [f"📋 <b>{record.title}</b>"]
    desc = vault_description(record)
    if desc:
        lines.append(f"<i>{t(lang, 'vlt_label_description')}</i>\n{desc}")
    if record.amount is not None:
        cur = record.currency or "UZS"
        lines.append(f"💰 <i>{t(lang, 'vlt_label_amount')}</i> {record.amount:,.0f} {cur}".replace(",", " "))
    if record_has_file(record):
        lines.append(f"📎 {t(lang, 'vlt_has_file')}")
    elif not desc and record.amount is None:
        lines.append(t(lang, "vlt_no_file_attached"))
    return "\n\n".join(lines)


def vault_description(record: LifeRecord) -> str:
    return vault_text_body(record)


def is_image_file(mime: str | None, *, kind: str | None = None) -> bool:
    if kind == "photo":
        return True
    if kind == "document":
        return False
    if mime:
        return mime.startswith("image/")
    return True


async def delete_vault_item(session: AsyncSession, user_id: int, record_id: int) -> bool:
    record = (
        await session.execute(
            select(LifeRecord).where(
                LifeRecord.id == record_id,
                LifeRecord.user_id == user_id,
                LifeRecord.module_id == VAULT_MODULE,
            )
        )
    ).scalar_one_or_none()
    if not record:
        return False
    await session.delete(record)
    await session.commit()
    return True


def format_vault_line(record: LifeRecord, submodule_id: str, *, lang: str = "ru") -> str:
    from app.core.i18n import t

    icon = SUBMODULE_ICONS.get(submodule_id, "🔐")
    line = f"{icon} <b>{record.title}</b>"
    if record.amount is not None:
        line += f" — {record.amount:,.0f} UZS".replace(",", " ")
    desc = vault_description(record)
    if desc:
        if submodule_id == "passport":
            line += f"\n  <i>🔒 {t(lang, 'vlt_passport_hidden')}</i>"
        else:
            line += f"\n  <i>{desc.replace(chr(10), ' ')[:70]}</i>"
    if record_has_file(record):
        line += "\n  📎"
    return line


def vault_submodule_title_key(sub_id: str) -> str:
    return f"vlt_{sub_id}_title"
