from app.services.openai_compat import chat_token_limit_kwargs


def test_old_model_uses_max_tokens():
    assert chat_token_limit_kwargs("gpt-4o-mini", 1200) == {"max_tokens": 1200}


def test_gpt5_uses_max_completion_tokens():
    assert chat_token_limit_kwargs("gpt-5-mini", 1200) == {"max_completion_tokens": 1200}


def test_o_series_uses_max_completion_tokens():
    assert chat_token_limit_kwargs("o3-mini", 800) == {"max_completion_tokens": 800}
