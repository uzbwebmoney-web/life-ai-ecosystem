from app.services.study_notes_service import (
    completion_limit_for_notes,
    parse_requested_pages,
    prepare_study_notes_request,
    study_notes_depth_instruction,
)


def test_parse_ten_pages():
    assert parse_requested_pages("конспект на 10 страниц по ИИ") == 10
    assert parse_requested_pages("10 страниц") == 10


def test_completion_limit_scales_with_pages():
    assert completion_limit_for_notes("конспект на 10 страниц") == 9000
    assert completion_limit_for_notes("кратко на 1 страницу") == 1800


def test_default_notes_limit():
    assert completion_limit_for_notes("конспект по физике") == 4500


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
