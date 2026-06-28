from __future__ import annotations

import io

from aiogram import Bot
from openai import AsyncOpenAI

from app.core.config import settings


async def transcribe_voice(bot: Bot, file_id: str) -> str:
    if not settings.openai_api_key.strip():
        return ""
    file = await bot.get_file(file_id)
    buffer = io.BytesIO()
    await bot.download_file(file.file_path, buffer)
    buffer.seek(0)
    buffer.name = "voice.ogg"
    client = AsyncOpenAI(api_key=settings.openai_api_key)
    result = await client.audio.transcriptions.create(model="whisper-1", file=buffer)
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


async def generate_image(prompt: str) -> bytes | None:
    if not settings.openai_api_key.strip():
        return None
    import base64

    client = AsyncOpenAI(api_key=settings.openai_api_key)
    response = await client.images.generate(
        model="dall-e-3",
        prompt=prompt[:4000],
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    data = response.data[0].b64_json if response.data else None
    return base64.b64decode(data) if data else None


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
