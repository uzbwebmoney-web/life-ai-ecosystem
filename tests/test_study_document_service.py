from app.services.education_service import EDUCATION_SUBMODULE_AI
from app.services.study_document_service import (
    build_document_bytes,
    detect_export_format,
    extract_document_title,
    get_last_study_document,
    is_format_only_request,
    store_last_study_document,
    strip_export_disclaimers,
)


def test_notes_prompt_allows_file_export():
    notes = EDUCATION_SUBMODULE_AI["notes"]
    assert "PDF" in notes
    assert "прикрепить" in notes.lower() or "файл" in notes.lower()


def test_detect_export_format():
    assert detect_export_format("конспект по ИИ в pdf") == "pdf"
    assert detect_export_format("оформи как word") == "docx"
    assert detect_export_format("отправь txt") == "txt"
    assert detect_export_format("просто конспект") is None


def test_is_format_only_request():
    assert is_format_only_request("сделай pdf")
    assert is_format_only_request("оформи в word пожалуйста")
    assert not is_format_only_request("конспект по физике в pdf для школы")


def test_strip_export_disclaimers():
    text = "Конспект.\n\nЕсли хочешь, я могу:\n- сделать pdf"
    cleaned = strip_export_disclaimers(text)
    assert "Если хочешь" not in cleaned
    assert cleaned.startswith("Конспект")


def test_extract_document_title():
    title = extract_document_title('Конспект по теме «Искусственный интеллект»', "1. Что такое ИИ")
    assert "Искусственный интеллект" in title


def test_build_document_bytes_all_formats():
    title = "Тест"
    body = "1. Пункт один\n- подпункт"
    for fmt in ("txt", "md", "docx", "pdf"):
        data, name = build_document_bytes(title, body, fmt)
        assert data
        assert name.endswith(f".{fmt}")


def test_study_document_cache():
    store_last_study_document(99, title="T", body="B", query="Q")
    cached = get_last_study_document(99)
    assert cached and cached["title"] == "T"
