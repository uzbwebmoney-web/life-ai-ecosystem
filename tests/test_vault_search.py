from app.models.entities import LifeRecord
from app.services.ecosystem_service import format_record_search_line
from app.services.vault_service import vault_search_tags


def test_vault_search_tags_contain_russian_keywords():
    tags = vault_search_tags("passport")
    assert "паспорт" in tags
    assert "passport" in tags


def test_format_record_search_line_shows_file_without_file_id():
    record = LifeRecord(
        module_id="vault",
        submodule_id="receipts",
        title="Чек — Фото",
        body="receipts chek чек\nfile_id=abc123\n\nМагазин X 150000 UZS",
    )
    line = format_record_search_line(record, "ru")
    assert "vault/receipts" in line
    assert "file_id=" not in line
    assert "Магазин" in line
