from app.services.admin_service import AdminStats, format_admin_stats_message, format_recent_users_message, parse_admin_telegram_ids


def test_admin_telegram_ids_parsing():
    assert parse_admin_telegram_ids("111, 222;333") == [111, 222, 333]


def test_format_admin_stats_message():
    stats = AdminStats(
        total_users=100,
        new_today=5,
        new_last_7_days=20,
        new_last_30_days=45,
        active_last_7_days=30,
        onboarding_completed=80,
        users_by_language={"ru": 70, "uz": 20, "en": 10},
        total_records=500,
        total_memory_entries=120,
        vault_protected_users=15,
    )
    text = format_admin_stats_message(stats, lang="ru")
    assert "100" in text
    assert "ru: 70" in text
    assert "500" in text


def test_format_recent_users_message():
    from datetime import datetime

    from app.models.entities import User

    users = [
        User(id=1, telegram_id=111, username="testuser", language="ru", onboarding_done=True),
    ]
    users[0].created_at = datetime(2026, 6, 23, 12, 0)
    text = format_recent_users_message(users, lang="ru")
    assert "testuser" in text
