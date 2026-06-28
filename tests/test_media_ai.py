from unittest.mock import Mock

from app.services.media_ai import (
    build_image_generate_kwargs,
    image_model_candidates,
    is_unsupported_image_model_error,
)


def test_image_model_candidates_deduplicates(monkeypatch):
    monkeypatch.setattr(
        "app.services.media_ai.settings.openai_image_model",
        "dall-e-3",
    )
    monkeypatch.setattr(
        "app.services.media_ai.settings.openai_image_model_fallbacks",
        "dall-e-2,dall-e-3,gpt-image-1",
    )
    assert image_model_candidates() == ["dall-e-3", "dall-e-2", "gpt-image-1"]


def test_build_image_generate_kwargs_dalle3():
    kwargs = build_image_generate_kwargs("dall-e-3", "cat")
    assert kwargs["model"] == "dall-e-3"
    assert kwargs["quality"] == "standard"
    assert kwargs["size"] == "1024x1024"


def test_build_image_generate_kwargs_gpt_image():
    kwargs = build_image_generate_kwargs("gpt-image-1", "cat", quality="high")
    assert kwargs["model"] == "gpt-image-1"
    assert kwargs["quality"] == "high"


def test_is_unsupported_image_model_error():
    exc = Mock()
    exc.body = {
        "error": {
            "message": "The model 'dall-e-3' does not exist.",
            "type": "image_generation_user_error",
            "param": "model",
            "code": "invalid_value",
        }
    }
    assert is_unsupported_image_model_error(exc)
