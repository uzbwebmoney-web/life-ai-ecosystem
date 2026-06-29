from datetime import datetime, timedelta

from app.models.entities import LifeRecord, User
from app.services.vault_lock_service import (
    filter_vault_records_for_search,
    hash_vault_password,
    is_vault_protected,
    is_vault_unlocked,
    lock_vault,
    lock_vault_on_menu_exit,
    unlock_vault,
    validate_password_strength,
    verify_vault_password,
)


def test_validate_password_strength():
    assert validate_password_strength("1234")
    assert not validate_password_strength("abc")
    assert not validate_password_strength("x" * 65)


def test_hash_and_verify_password():
    user = User(id=1, telegram_id=1, vault_password_hash=hash_vault_password("secret123"))
    assert verify_vault_password(user, "secret123")
    assert not verify_vault_password(user, "wrong")


def test_is_vault_protected():
    assert not is_vault_protected(User(id=1, telegram_id=1))
    assert is_vault_protected(User(id=1, telegram_id=1, vault_password_hash="hash"))


def test_unlock_session_ttl():
    user = User(id=42, telegram_id=42)
    lock_vault(user)
    assert not is_vault_unlocked(user)
    unlock_vault(user)
    user.vault_unlocked_until = datetime.utcnow() - timedelta(seconds=1)
    assert not is_vault_unlocked(user)


def test_lock_vault_on_menu_exit():
    user = User(id=5, telegram_id=5, vault_password_hash="hash")
    unlock_vault(user)
    assert is_vault_unlocked(user)
    lock_vault_on_menu_exit(user)
    assert not is_vault_unlocked(user)
    lock_vault_on_menu_exit(User(id=6, telegram_id=6))


def test_filter_vault_records_for_search():
    user = User(id=1, telegram_id=1, vault_password_hash=hash_vault_password("1234"))
    vault_rec = LifeRecord(id=1, user_id=1, module_id="vault", submodule_id="notes", title="Secret")
    car_rec = LifeRecord(id=2, user_id=1, module_id="car", submodule_id="maint", title="Oil")
    unlock_vault(user)
    visible, hidden = filter_vault_records_for_search(user, [vault_rec, car_rec])
    assert len(visible) == 2
    assert hidden == 0
    lock_vault(user)
    visible, hidden = filter_vault_records_for_search(user, [vault_rec, car_rec])
    assert len(visible) == 1
    assert visible[0].module_id == "car"
    assert hidden == 1
