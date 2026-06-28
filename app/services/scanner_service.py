from __future__ import annotations

import json
import re

from app.core.i18n import ai_reply_language

ARCHIVE_FOLDERS: tuple[str, ...] = (
    "passport",
    "car",
    "contracts",
    "analyses",
    "receipts",
    "photos",
    "warranty",
)

ARCHIVE_FOLDER_LABELS: dict[str, dict[str, str]] = {
    "passport": {"ru": "📁 Паспорт", "uz": "📁 Pasport", "en": "📁 Passport"},
    "car": {"ru": "📁 Машина", "uz": "📁 Avto", "en": "📁 Car"},
    "contracts": {"ru": "📁 Договоры", "uz": "📁 Shartnomalar", "en": "📁 Contracts"},
    "analyses": {"ru": "📁 Анализы", "uz": "📁 Tahlillar", "en": "📁 Lab tests"},
    "receipts": {"ru": "📁 Чеки", "uz": "📁 Cheklar", "en": "📁 Receipts"},
    "photos": {"ru": "📁 Фото", "uz": "📁 Foto", "en": "📁 Photos"},
    "warranty": {"ru": "📁 Гарантии", "uz": "📁 Kafolat", "en": "📁 Warranty"},
}


def universal_scan_prompt(lang: str, caption: str = "") -> str:
    reply_lang = ai_reply_language(lang)
    prompt = (
        "Universal life scanner. Identify what this image is: receipt, prescription, lab test, "
        "contract, passport, car dashboard error, utility bill, warranty, food/fridge contents, other. "
        "Extract key data (amounts, dates, names). "
        "If fridge/food — list visible products briefly. "
        f"Reply in {reply_lang}."
    )
    if caption:
        prompt += f"\nUser note: {caption}"
    return prompt


def classify_scan(analysis: str, caption: str = "") -> tuple[str, str, str]:
    combined = f"{caption} {analysis}".lower()
    folder = "photos"
    module_id, sub_id = "vault", "documents"

    if any(x in combined for x in ("паспорт", "passport", "pasport")):
        folder, module_id, sub_id = "passport", "vault", "passport"
    elif any(x in combined for x in ("чек", "receipt", "chek", "касс", "summa", "uzs", "сум")):
        folder, module_id, sub_id = "receipts", "vault", "receipts"
    elif any(x in combined for x in ("анализ", "tahlil", "lab", "blood", "qon", "medical")):
        folder, module_id, sub_id = "analyses", "health", "documents"
    elif any(x in combined for x in ("договор", "contract", "shartnoma", "agreement")):
        folder, module_id, sub_id = "contracts", "vault", "documents"
    elif any(x in combined for x in ("гарант", "warranty", "kafolat")):
        folder, module_id, sub_id = "warranty", "vault", "warranty"
    elif any(x in combined for x in ("ошибк", "error", "obd", "dashboard", "check engine", "panel")):
        folder, module_id, sub_id = "car", "car", "panel_photo"
    elif any(x in combined for x in ("полис", "страхов", "insurance", "sug'urta")):
        folder, module_id, sub_id = "car", "car", "compliance"
    elif any(x in combined for x in ("рецепт", "prescription", "dori", "лекарств", "medicine")):
        folder, module_id, sub_id = "analyses", "health", "medicines"
    elif any(x in combined for x in ("холодильник", "fridge", "продукт", "recipe", "retsept", "ovqat")):
        folder, module_id, sub_id = "photos", "nutrition", "recipes"

    return module_id, sub_id, folder


def archive_meta(folder: str, *, scan: bool = True) -> str:
    return json.dumps({"archive_folder": folder, "auto_scan": scan}, ensure_ascii=False)


def parse_amount_from_text(text: str) -> float | None:
    for pattern in (r"(\d[\d\s]{2,})\s*(?:uzs|сум|sum|so'm)", r"(?:amount|сумма|summa)[:\s]+(\d[\d\s,]*)"):
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            raw = match.group(1).replace(" ", "").replace(",", "")
            try:
                return float(raw)
            except ValueError:
                continue
    return None


def archive_label(folder: str, lang: str) -> str:
    labels = ARCHIVE_FOLDER_LABELS.get(folder, {})
    return labels.get(lang, labels.get("ru", f"📁 {folder}"))
