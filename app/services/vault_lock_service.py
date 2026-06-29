from __future__ import annotations

import time
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User

UNLOCK_TTL_SECONDS = 30 * 60
MIN_PASSWORD_LEN = 4
MAX_PASSWORD_LEN = 64
MAX_UNLOCK_ATTEMPTS = 5
ATTEMPT_WINDOW_SECONDS = 15 * 60

_unlocked_until: dict[int, float] = {}
_failed_attempts: dict[int, list[float]] = {}


def is_vault_protected(user: User) -> bool:
    return bool(user.vault_password_hash)


def _memory_unlocked(user_id: int) -> bool:
    expires = _unlocked_until.get(user_id)
    if not expires:
        return False
    if time.time() >= expires:
        _unlocked_until.pop(user_id, None)
        return False
    return True


def is_vault_unlocked(user: User) -> bool:
    if user.vault_unlocked_until and user.vault_unlocked_until > datetime.utcnow():
        return True
    return _memory_unlocked(user.id)


def unlock_vault(user: User) -> datetime:
    until = datetime.utcnow() + timedelta(seconds=UNLOCK_TTL_SECONDS)
    user.vault_unlocked_until = until
    _unlocked_until[user.id] = until.timestamp()
    _failed_attempts.pop(user.id, None)
    return until


def lock_vault(user: User) -> None:
    user.vault_unlocked_until = None
    _unlocked_until.pop(user.id, None)


def lock_vault_on_menu_exit(user: User) -> None:
    if is_vault_protected(user):
        lock_vault(user)


def validate_password_strength(password: str) -> bool:
    return MIN_PASSWORD_LEN <= len(password) <= MAX_PASSWORD_LEN


def vault_unlock_rate_limited(user_id: int) -> bool:
    now = time.time()
    window_start = now - ATTEMPT_WINDOW_SECONDS
    attempts = [ts for ts in _failed_attempts.get(user_id, []) if ts >= window_start]
    _failed_attempts[user_id] = attempts
    return len(attempts) >= MAX_UNLOCK_ATTEMPTS


def record_vault_unlock_failure(user_id: int) -> None:
    _failed_attempts.setdefault(user_id, []).append(time.time())


def hash_vault_password(password: str) -> str:
    import hashlib
    import secrets as sec

    salt = sec.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_vault_password(user: User, password: str) -> bool:
    stored = user.vault_password_hash
    if not stored:
        return False
    try:
        import hashlib
        import secrets as sec

        scheme, iterations, salt, expected = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        return sec.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False


async def set_vault_password(session: AsyncSession, user: User, password: str) -> None:
    user.vault_password_hash = hash_vault_password(password)
    unlock_vault(user)
    await session.commit()


async def clear_vault_password(session: AsyncSession, user: User) -> None:
    user.vault_password_hash = None
    lock_vault(user)
    await session.commit()


def filter_vault_records_for_search(
    user: User,
    records: list,
) -> tuple[list, int]:
    from app.services.vault_service import VAULT_MODULE

    if not is_vault_protected(user) or is_vault_unlocked(user):
        return records, 0
    visible = [
        r
        for r in records
        if not (getattr(r, "module_id", None) == VAULT_MODULE and getattr(r, "user_id", None) == user.id)
    ]
    return visible, len(records) - len(visible)
