from app.services.study_notes_service import (
    completion_limit_for_notes,
    effective_page_count,
    needs_study_document_clarification,
    parse_requested_pages,
    prepare_study_notes_request,
    study_notes_depth_instruction,
)
from app.services.text_format import escape_telegram_html, format_ai_reply


def test_parse_ten_pages():
    assert parse_requested_pages("конспект на 10 страниц по ИИ") == 10
    assert parse_requested_pages("10 страниц") == 10
    assert parse_requested_pages("10 bet PDF") == 10


def test_completion_limit_scales_with_pages():
    assert completion_limit_for_notes("конспект на 10 страниц") == 9000
    assert completion_limit_for_notes("кратко на 1 страницу") == 1800


def test_voluminous_defaults_to_ten_pages():
    assert effective_page_count("katta referat sun'iy intellekt haqida") == 10
    assert completion_limit_for_notes("katta batafsil referat") == 9000


def test_mega_voluminous_defaults_to_fifteen_pages():
    assert effective_page_count("juda ko'p bet referat") == 15
    assert completion_limit_for_notes("juda ko'p bet referat") == 13500


def test_prepare_study_notes_request():
    msg, hint, limit = prepare_study_notes_request(
        "education",
        "notes",
        "конспект на 10 страниц по ИИ",
        "base hint",
    )
    assert msg.startswith("конспект")
    assert "10 страниц" in hint
    assert limit == 9000


def test_prepare_other_module_unchanged():
    msg, hint, limit = prepare_study_notes_request("finance", None, "test", "hint")
    assert limit == 1200
    assert hint == "hint"


def test_needs_clarification_for_referat_without_params():
    assert needs_study_document_clarification("education", "notes", "referat sun'iy intellekt haqida")


def test_no_clarification_when_voluminous():
    assert not needs_study_document_clarification("education", "notes", "katta batafsil referat")


def test_no_clarification_when_pages_given():
    text = "referat sun'iy intellekt, 10 bet"
    assert not needs_study_document_clarification("education", "notes", text)


def test_escape_telegram_html():
    assert escape_telegram_html("a < b & c") == "a &lt; b &amp; c"


def test_format_ai_reply_strips_bold():
    assert format_ai_reply("**test**") == "test"
