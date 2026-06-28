from __future__ import annotations

import logging

import httpx

from app.core.i18n import t

logger = logging.getLogger(__name__)

# Approximate city coords by UTC offset (minutes east of UTC)
_OFFSET_COORDS: dict[int, tuple[float, float]] = {
    180: (43.238, 76.945),   # Almaty UTC+6
    300: (41.2995, 69.2401),  # Tashkent UTC+5
    240: (41.311, 69.279),    # Samarkand UTC+4
    0: (51.507, -0.128),      # London
    -300: (40.713, -74.006),  # New York
}


def coords_for_offset(utc_offset_minutes: int) -> tuple[float, float]:
    return _OFFSET_COORDS.get(utc_offset_minutes, _OFFSET_COORDS[300])


async def fetch_weather_summary(*, lang: str = "ru", utc_offset_minutes: int = 300) -> str:
    lat, lon = coords_for_offset(utc_offset_minutes)
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
        return t(lang, "weather_unavailable")
    current = data.get("current") or {}
    daily = data.get("daily") or {}
    temp = current.get("temperature_2m")
    humidity = current.get("relative_humidity_2m")
    wind = current.get("wind_speed_10m")
    uv = (daily.get("uv_index_max") or [None])[0]
    tmax = (daily.get("temperature_2m_max") or [None])[0]
    tmin = (daily.get("temperature_2m_min") or [None])[0]
    uv_str = str(uv) if uv is not None else "—"
    return (
        f"{t(lang, 'weather_now', temp=temp, humidity=humidity, wind=wind)}\n"
        f"{t(lang, 'weather_today_range', tmin=tmin, tmax=tmax)}\n"
        f"{t(lang, 'weather_uv', uv=uv_str)}"
    )
