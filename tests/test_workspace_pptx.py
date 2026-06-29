from app.services.table_export_service import build_pptx_bytes, slides_from_text
from app.services.workspace_rag_service import extract_text_from_bytes, _chunk_text, _score_chunk
from app.services.agent.planner import build_plan_rule_based
from app.services.study_document_service import detect_export_format


def test_detect_export_pptx():
    assert detect_export_format("сделай презентацию pptx") == "pptx"


def test_build_pptx_bytes():
    slides = [("Intro", "Point one\nPoint two"), ("Summary", "Conclusion")]
    data, name = build_pptx_bytes("Test", slides)
    assert name.endswith(".pptx")
    assert len(data) > 1000
    assert data[:2] == b"PK"


def test_slides_from_text():
    text = "# Title\n## Slide 1\nBullet A\n## Slide 2\nBullet B"
    slides = slides_from_text(text, default_title="Title")
    assert len(slides) >= 2


def test_extract_text_plain():
    text = extract_text_from_bytes(b"Hello workspace", filename="note.txt")
    assert "Hello" in text


def test_chunk_and_score():
    chunks = _chunk_text("alpha beta gamma " * 20)
    assert len(chunks) >= 1
    assert _score_chunk("beta", "alpha beta text") >= 1


def test_plan_presentation():
    plan = build_plan_rule_based("Сделай презентацию pptx по теме AI")
    assert plan is not None
    assert plan.intent == "presentation"
