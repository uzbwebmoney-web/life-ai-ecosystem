from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass
class FileClassification:
    doc_type: str
    primary_module: str
    submodule: str
    folder: str
    related_modules: list[str] = field(default_factory=list)
    keywords: list[str] = field(default_factory=list)


_RECEIPT = re.compile(r"\b(?:чек|receipt|chek|xarajat|invoice|сч[её]т)\b", re.I)
_WARRANTY = re.compile(r"\b(?:гарант|warranty|kafolat)\b", re.I)
_PASSPORT = re.compile(r"\b(?:паспорт|passport|visa|виза)\b", re.I)
_MEDICAL = re.compile(r"\b(?:анализ|analysis|tahlil|blood|lab|medical|рецепт|prescription)\b", re.I)
_CONTRACT = re.compile(r"\b(?:договор|contract|shartnoma|policy|полис)\b", re.I)
_APPLIANCE = re.compile(r"\b(?:холодильник|fridge|техник|appliance|washer|стирал)\b", re.I)
_CAR = re.compile(r"\b(?:obd|check engine|dashboard|ошибк|error code|vin)\b", re.I)


def classify_upload(text: str, *, caption: str = "") -> FileClassification:
    combined = f"{caption}\n{text}".lower()
    keywords: list[str] = []
    related: list[str] = []

    if _RECEIPT.search(combined):
        keywords.extend(["receipt", "чек"])
        related = ["vault", "finance", "home"]
        return FileClassification(
            doc_type="receipt",
            primary_module="vault",
            submodule="receipts",
            folder="receipts",
            related_modules=related,
            keywords=keywords,
        )

    if _WARRANTY.search(combined):
        related = ["vault", "finance", "home"]
        return FileClassification(
            doc_type="warranty",
            primary_module="vault",
            submodule="warranty",
            folder="warranty",
            related_modules=related,
            keywords=["warranty", "гарантия"],
        )

    if _PASSPORT.search(combined):
        return FileClassification(
            doc_type="passport",
            primary_module="vault",
            submodule="passport",
            folder="passport",
            related_modules=["vault", "travel"],
            keywords=["passport", "паспорт"],
        )

    if _MEDICAL.search(combined):
        return FileClassification(
            doc_type="medical",
            primary_module="health",
            submodule="documents",
            folder="analyses",
            related_modules=["health", "vault"],
            keywords=["medical", "анализ"],
        )

    if _CONTRACT.search(combined):
        return FileClassification(
            doc_type="contract",
            primary_module="legal",
            submodule="doc_check",
            folder="contracts",
            related_modules=["legal", "vault"],
            keywords=["contract", "договор"],
        )

    if _APPLIANCE.search(combined):
        return FileClassification(
            doc_type="appliance",
            primary_module="home",
            submodule="inventory",
            folder="home",
            related_modules=["home", "vault", "finance"],
            keywords=["appliance", "техника"],
        )

    if _CAR.search(combined):
        return FileClassification(
            doc_type="car",
            primary_module="car",
            submodule="panel_photo",
            folder="car",
            related_modules=["car", "vault"],
            keywords=["car", "auto"],
        )

    return FileClassification(
        doc_type="document",
        primary_module="vault",
        submodule="documents",
        folder="documents",
        related_modules=["vault"],
        keywords=["document"],
    )


def format_related_modules_hint(classification: FileClassification, lang: str = "ru") -> str:
    from app.core.i18n import t

    if len(classification.related_modules) <= 1:
        return ""
    mods = ", ".join(classification.related_modules)
    return t(lang, "uni_file_modules", modules=mods)
