from app.services.nutrition_service import ACTIVITY_FACTORS, NUTRITION_SUBMODULE_AI, calculate_tdee, parse_int_amount


def test_nutrition_ai_hints():
    assert len(NUTRITION_SUBMODULE_AI) == 3
    assert "recipes" in NUTRITION_SUBMODULE_AI


def test_calculate_tdee():
    kcal = calculate_tdee(weight_kg=70, height_cm=175, age=30, sex="male", activity="moderate")
    assert 2000 < kcal < 3500


def test_activity_factors():
    assert ACTIVITY_FACTORS["sedentary"] == 1.2


def test_parse_int_amount():
    assert parse_int_amount("250") == 250
    assert parse_int_amount("abc") is None
