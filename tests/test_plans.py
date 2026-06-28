from app.core.plans import ADDON_PACKAGES, ai_request_weight


def test_ai_request_weights():
    assert ai_request_weight("gpt-4o-mini") == 1
    assert ai_request_weight("gpt-5.4-mini") == 5
    assert ai_request_weight("gpt-5.5") == 20


def test_addon_packages():
    assert len(ADDON_PACKAGES) == 4
    pkg_ids = {p.id for p in ADDON_PACKAGES}
    assert pkg_ids == {"p_img50", "p_gpt54_500", "p_gpt55_50", "p_cloud20"}
