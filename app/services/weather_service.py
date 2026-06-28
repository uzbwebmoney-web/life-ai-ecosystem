from __future__ import annotations

import logging

import httpx

logger = logging.getLogger(__name__)

DEFAULT_LAT = 41.2995
DEFAULT_LON = 69.2401


async def fetch_weather_summary(*, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON) -> str:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,uv_index_max",
        "timezone": "auto",
        "forecast_days": 1,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()
    except Exception:
        logger.exception("Weather fetch failed")
        return "Погода временно недоступна."
    current = data.get("current") or {}
    daily = (data.get("daily") or {})
    t = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    uv = (daily.get("uv_index_max") or [None])[0]
    tmax = (daily.get("temperature_2m_max") or [None])[0]
    tmin = (daily.get("temperature_2m_min") or [None])[0]
    return (
        f"🌤 Сейчас: {t}°C, влажность {humidity}%, ветер {wind} м/с\n"
        f"📈 Сегодня: {tmin}°…{tmax}°C\n"
        f"☀️ UV-индекс: {uv if uv is not None else '—'}"
    )
