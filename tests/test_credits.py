from app.core.credits import (
    ACTION_CREDITS,
    apply_internal_coefficients,
    estimate_request_credits,
    image_generation_credits,
    photo_analysis_credits,
    study_notes_credits,
)
from app.core.plans import PLANS
from app.services.model_router import QueryComplexity


def test_action_credits_table():
    assert ACTION_CREDITS["simple"] == 1
    assert ACTION_CREDITS["translation"] == 1
    assert ACTION_CREDITS["health"] == 2
    assert ACTION_CREDITS["legal"] == 3
    assert ACTION_CREDITS["code"] == 5
    assert ACTION_CREDITS["notes_10p"] == 15
    assert ACTION_CREDITS["notes_50p"] == 70


def test_study_notes_credits():
    assert study_notes_credits("кратко на 1 страницу") == 1
    assert study_notes_credits("конспект по физике") == 6
    assert study_notes_credits("katta batafsil referat") == 10
    assert study_notes_credits("конспект на 10 страниц") == 15
    assert study_notes_credits("конспект на 50 страниц") == 70


def test_image_and_photo_credits():
    assert image_generation_credits("low") == 15
    assert image_generation_credits("medium") == 30
    assert image_generation_credits("high") == 60
    assert photo_analysis_credits() == 4


def test_internal_model_coefficient():
    base = apply_internal_coefficients(10, model="gpt-4o-mini", max_output_tokens=3000)
    advanced = apply_internal_coefficients(10, model="gpt-5.4-mini", max_output_tokens=3000)
    pro = apply_internal_coefficients(10, model="gpt-5.5", max_output_tokens=3000)
    assert base == 10
    assert advanced == 11
    assert pro == 13


def test_module_health_cost():
    est = estimate_request_credits(
        user_message="болит голова",
        model="gpt-4o-mini",
        max_output_tokens=1200,
        module_id="health",
        submodule_id="symptoms",
        complexity=QueryComplexity.STANDARD,
    )
    assert est.credits == 2


def test_plan_credit_limits():
    assert PLANS["free"].limits.ai_credits_monthly == 300
    assert PLANS["student"].limits.ai_credits_monthly == 1500
    assert PLANS["basic"].limits.ai_credits_monthly == 5000
    assert PLANS["premium"].limits.ai_credits_monthly == 15000
    assert PLANS["pro"].limits.ai_credits_monthly == 40000


def test_plan_prices():
    assert PLANS["student"].usd_monthly == 2.99
    assert PLANS["basic"].usd_monthly == 5.99
    assert PLANS["premium"].usd_monthly == 11.99
    assert PLANS["pro"].usd_monthly == 19.99
