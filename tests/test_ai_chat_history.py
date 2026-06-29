from app.services.ai_chat_history import append_turn, module_history_key, normalize_history, serialize_history
from app.services.travel_service import TRAVEL_SUBMODULE_AI


def test_travel_visas_hint_defaults_uzbekistan() -> None:
    hint = TRAVEL_SUBMODULE_AI["visas"].lower()
    assert "узбекистан" in hint
    assert "не подставляй россию" in hint


def test_chat_history_keeps_context_chain() -> None:
    history = normalize_history([])
    history = append_turn(history, "виза для Мальдив", "Для граждан Узбекистана виза не нужна на 30 дней.")
    history = append_turn(history, "а для узбекистана?", "Уточните вопрос")
    assert len(history) == 2
    assert "мальдив" in history[0][0].lower()
    assert "узбекистан" in history[0][1].lower()


def test_module_history_key_scoped() -> None:
    assert module_history_key("travel", "visas") == "mod_chat:travel:visas"
    assert module_history_key("travel", None) == "mod_chat:travel:"


def test_serialize_roundtrip() -> None:
    raw = serialize_history([("q1", "a1")])
    restored = normalize_history(raw)
    assert restored == [("q1", "a1")]
