from __future__ import annotations

import io
import logging

from aiogram import Bot
from openai import AsyncOpenAI, BadRequestError

from app.core.config import settings

logger = logging.getLogger(__name__)


_DEPRECATED_IMAGE_MODELS = frozenset({"dall-e-3"})


def image_model_candidates() -> list[str]:
    primary = (settings.openai_image_model or "gpt-image-1").strip()
    if primary.lower() in _DEPRECATED_IMAGE_MODELS:
        primary = "gpt-image-1"
    raw_fallbacks = (settings.openai_image_model_fallbacks or "").strip()
    fallbacks = [
        part.strip()
        for part in raw_fallbacks.split(",")
        if part.strip() and part.strip().lower() not in _DEPRECATED_IMAGE_MODELS
    ]
    if not fallbacks:
        fallbacks = ["dall-e-2"]
    seen: set[str] = set()
    ordered: list[str] = []
    for model in [primary, *fallbacks]:
        key = model.lower()
        if key in seen:
            continue
        seen.add(key)
        ordered.append(model)
    return ordered


def build_image_generate_kwargs(model: str | None, prompt: str, *, quality: str = "medium") -> dict:
    kwargs: dict = {"prompt": prompt[:4000], "n": 1}
    if model:
        kwargs["model"] = model
    name = (model or "gpt-image-1").lower()
    kwargs["size"] = "1024x1024"
    if name.startswith("gpt-image"):
        q = quality if quality in {"low", "medium", "high"} else "medium"
        kwargs["quality"] = q
    elif name == "dall-e-3":
        kwargs["quality"] = "standard"
    return kwargs


def is_unsupported_image_model_error(exc: BadRequestError) -> bool:
    body = getattr(exc, "body", None) or {}
    err = body.get("error", {}) if isinstance(body, dict) else {}
    code = str(err.get("code") or "").lower()
    param = str(err.get("param") or "").lower()
    message = str(err.get("message") or exc).lower()
    if param == "model" and code in {"invalid_value", "model_not_found"}:
        return True
    return "does not exist" in message and "model" in message


async def transcribe_voice(bot: Bot, file_id: str) -> str:
    if not settings.openai_api_key.strip():
        return ""
    file = await bot.get_file(file_id)
    buffer = io.BytesIO()
    await bot.download_file(file.file_path, buffer)
    buffer.seek(0)
    buffer.name = "voice.ogg"
    return await transcribe_audio_buffer(buffer, prompt="")


async def transcribe_audio_bytes(
    data: bytes,
    filename: str,
    *,
    prompt: str = "",
) -> str:
    buffer = io.BytesIO(data)
    buffer.name = filename or "audio.mp3"
    return await transcribe_audio_buffer(buffer, prompt=prompt)


async def transcribe_audio_buffer(buffer: io.BytesIO, *, prompt: str = "") -> str:
    if not settings.openai_api_key.strip():
        return ""
    buffer.seek(0)
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    kwargs: dict = {"model": "whisper-1", "file": buffer}
    if prompt:
        kwargs["prompt"] = prompt[:200]
    result = await client.audio.transcriptions.create(**kwargs)
    return (result.text or "").strip()


async def analyze_image_url(
    image_url: str,
    prompt: str,
    *,
    model: str | None = None,
    session=None,
    user_id: int | None = None,
    user=None,
    bot: Bot | None = None,
) -> str:
    if not settings.openai_api_key.strip():
        return "⚠️ OPENAI_API_KEY не задан — OCR/vision недоступен."
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    from app.services.openai_compat import chat_token_limit_kwargs

    use_model = model or settings.openai_model
    response = await client.chat.completions.create(
        model=use_model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        **chat_token_limit_kwargs(use_model, 1500),
    )
    if session is not None and user_id is not None:
        from app.services.ai_usage_service import extract_usage, record_ai_usage

        await record_ai_usage(session, user_id, use_model, response, source="vision")
        if bot is not None and user is not None:
            from app.services.admin_notify_service import notify_admins_ai_request

            prompt_tokens, completion_tokens = extract_usage(response)
            await notify_admins_ai_request(
                bot,
                user,
                model=use_model,
                source="vision",
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                preview=prompt,
            )
    from app.services.text_format import format_ai_reply

    return format_ai_reply((response.choices[0].message.content or "").strip())


async def get_telegram_image_url(bot: Bot, file_id: str) -> str:
    file = await bot.get_file(file_id)
    return f"https://api.telegram.org/file/bot{settings.bot_token}/{file.file_path}"


async def _image_bytes_from_response(response) -> bytes | None:
    import base64

    import httpx

    if not response.data:
        return None
    item = response.data[0]
    if getattr(item, "b64_json", None):
        return base64.b64decode(item.b64_json)
    url = getattr(item, "url", None)
    if not url:
        return None
    async with httpx.AsyncClient(timeout=60) as http:
        resp = await http.get(url)
        resp.raise_for_status()
        return resp.content


async def generate_image(prompt: str, *, quality: str = "medium") -> tuple[bytes, str, object] | None:
    if not settings.openai_api_key.strip():
        return None

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    models = image_model_candidates()
    last_error: Exception | None = None

    for model in models:
        try:
            response = await client.images.generate(
                **build_image_generate_kwargs(model, prompt, quality=quality)
            )
            data = await _image_bytes_from_response(response)
            if data:
                if model != models[0]:
                    logger.info("Image generated with fallback model %s (primary: %s)", model, models[0])
                return data, model, response
        except BadRequestError as exc:
            last_error = exc
            if is_unsupported_image_model_error(exc):
                logger.warning("Image model %s unavailable: %s", model, exc)
                continue
            logger.exception("Image generation failed for model %s", model)
            return None
        except Exception:
            logger.exception("Image generation failed for model %s", model)
            return None

    if last_error:
        logger.error("All image models failed: %s", ", ".join(models))
    return None


async def synthesize_speech(text: str, *, voice: str = "alloy") -> bytes | None:
    if not settings.openai_api_key.strip():
        return None
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text[:500],
    )
    return response.content
