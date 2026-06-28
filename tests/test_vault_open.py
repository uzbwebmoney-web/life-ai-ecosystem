from app.models.entities import LifeRecord
from app.services.vault_service import is_image_file, parse_stored_file, vault_search_tags, vault_text_body


def test_parse_stored_file_photo():
    record = LifeRecord(body="tags\nfile_id=ABC123\n\nReceipt text")
    assert parse_stored_file(record) == ("ABC123", None)


def test_parse_stored_file_document():
    record = LifeRecord(body="file_id=DOC99\nmime=application/pdf")
    assert parse_stored_file(record) == ("DOC99", "application/pdf")


def test_vault_text_body_note():
    tags = vault_search_tags("notes")
    record = LifeRecord(submodule_id="notes", body=f"{tags}\nMy warranty until 2027")
    assert vault_text_body(record) == "My warranty until 2027"


def test_vault_text_body_with_analysis():
    record = LifeRecord(body="file_id=x\n\nShop receipt 100000 UZS")
    assert "100000" in vault_text_body(record)


def test_is_image_file():
    assert is_image_file("image/jpeg")
    assert not is_image_file("application/pdf")
