import json

from app.models.entities import LifeRecord
from app.services.vault_service import (
    format_vault_text_view,
    is_image_file,
    parse_stored_file,
    record_has_file,
    vault_file_meta,
    vault_search_tags,
    vault_text_body,
)


def test_parse_stored_file_photo():
    record = LifeRecord(body="tags\nfile_id=ABC123\n\nReceipt text")
    assert parse_stored_file(record) == ("ABC123", None, "photo")


def test_parse_stored_file_from_meta_json():
    meta = vault_file_meta("receipts", "TG999", folder="receipts")
    record = LifeRecord(body="receipts chek", meta_json=meta)
    assert parse_stored_file(record) == ("TG999", None, "photo")
    assert record_has_file(record)


def test_parse_stored_file_document():
    record = LifeRecord(body="file_id=DOC99\nmime=application/pdf")
    assert parse_stored_file(record) == ("DOC99", "application/pdf", "document")


def test_vault_text_body_note():
    tags = vault_search_tags("notes")
    record = LifeRecord(submodule_id="notes", body=f"{tags}\nMy warranty until 2027")
    assert vault_text_body(record) == "My warranty until 2027"


def test_vault_text_body_with_analysis():
    record = LifeRecord(body="file_id=x\n\nShop receipt 100000 UZS")
    assert "100000" in vault_text_body(record)


def test_format_vault_text_view_text_receipt():
    record = LifeRecord(title="Magnum", amount=150000.0, submodule_id="receipts", body=vault_search_tags("receipts"))
    text = format_vault_text_view(record, "ru")
    assert "Magnum" in text
    assert "150" in text


def test_is_image_file():
    assert is_image_file("image/jpeg", kind="photo")
    assert not is_image_file("application/pdf", kind="document")
