from app.services.proactive_service import suggest_actions


def test_turizm_does_not_trigger_travel_buttons():
    text = "Sun'iy intellekt turizm va moliya sohalarida qo'llaniladi."
    actions = suggest_actions(text, text, lang="uz")
    assert not any(a.action_id.startswith("travel") for a in actions)


def test_travel_still_detected():
    text = "Keyingi oy Istanbulga sayohat rejalashtirmoqchiman"
    actions = suggest_actions(text, "", lang="uz")
    assert any(a.action_id == "travel_plan" for a in actions)


def test_education_module_skips_proactive():
    text = "Keyingi oy Istanbulga sayohat"
    actions = suggest_actions(text, "", lang="ru", module_id="education")
    assert actions == []
