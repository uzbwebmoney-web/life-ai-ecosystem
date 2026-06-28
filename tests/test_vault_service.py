from app.models.entities import LifeRecord
from app.services.vault_service import (
    SUBMODULE_ICONS,
    VAULT_FILE_SUBMODULES,
    VAULT_MODULE,
    VAULT_SUBMODULES,
    format_vault_line,
    vault_submodule_title_key,
)


def test_vault_constants():
    assert VAULT_MODULE == "vault"
    assert len(VAULT_SUBMODULES) == 6
    assert "passport" in VAULT_SUBMODULES
    assert "receipts" in VAULT_FILE_SUBMODULES
    assert "notes" not in VAULT_FILE_SUBMODULES


def test_format_vault_line_masks_passport():
    record = LifeRecord(title="Загранпаспорт", body="1234 567890")
    line = format_vault_line(record, "passport")
    assert "Загранпаспорт" in line
    assert "567890" not in line
    assert "скрыты" in line or "yashir" in line or "hidden" in line.lower()


def test_format_vault_line_receipt_amount():
    record = LifeRecord(title="Магнит", body="", amount=150000.0)
    line = format_vault_line(record, "receipts")
    assert "Магнит" in line
    assert "150" in line


def test_vault_submodule_title_keys():
    assert vault_submodule_title_key("documents") == "vlt_documents_title"
    assert SUBMODULE_ICONS["policies"] == "📋"
