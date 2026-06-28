from __future__ import annotations

import hashlib
import secrets
import time

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.entities import User

UNLOCK_TTL_SECONDS = 30 * 60
MIN_PASSWORD_LEN = 4
MAX_PASSWORD_LEN = 64

_unlocked_until: dict[int, float] = {}


def is_vault_protected(user: User) -> bool:
    return bool(user.vault_password_hash)


def is_vault_unlocked(user_id: int) -> bool:
    expires = _unlocked_until.get(user_id)
    if not expires:
        return False
    if time.time() >= expires:
        _unlocked_until.pop(user_id, None)
        return False
    return True


def unlock_vault(user_id: int, *, ttl_seconds: int = UNLOCK_TTL_SECONDS) -> None:
    _unlocked_until[user_id] = time.time() + ttl_seconds


def lock_vault(user_id: int) -> None:
    _unlocked_until.pop(user_id, None)


def lock_vault_on_menu_exit(user: User) -> None:
    if is_vault_protected(user):
        lock_vault(user.id)


def validate_password_strength(password: str) -> bool:
    return MIN_PASSWORD_LEN <= len(password) <= MAX_PASSWORD_LEN


def hash_vault_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt.encode("utf-8"), 120_000)
    return f"pbkdf2_sha256$120000${salt}${digest.hex()}"


def verify_vault_password(user: User, password: str) -> bool:
    stored = user.vault_password_hash
    if not stored:
        return False
    try:
        scheme, iterations, salt, expected = stored.split("$", 3)
        if scheme != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt.encode("utf-8"),
            int(iterations),
        )
        return secrets.compare_digest(digest.hex(), expected)
    except (ValueError, TypeError):
        return False


async def set_vault_password(session: AsyncSession, user: User, password: str) -> None:
    user.vault_password_hash = hash_vault_password(password)
    await session.commit()
    unlock_vault(user.id)


async def clear_vault_password(session: AsyncSession, user: User) -> None:
    user.vault_password_hash = None
    await session.commit()
    lock_vault(user.id)


def filter_vault_records_for_search(
    user: User,
    records: list,
) -> tuple[list, int]:
    from app.services.vault_service import VAULT_MODULE

    if not is_vault_protected(user) or is_vault_unlocked(user.id):
        return records, 0
    visible = [
        r
        for r in records
        if not (getattr(r, "module_id", None) == VAULT_MODULE and getattr(r, "user_id", None) == user.id)
    ]
    return visible, len(records) - len(visible)
