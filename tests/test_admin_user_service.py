from app.services.admin_user_service import parse_user_search_query, search_users


def test_parse_user_search_query():
    assert parse_user_search_query("@tester")[0] == "username"
    assert parse_user_search_query("12345")[0] == "numeric"
    assert parse_user_search_query("")[0] == "empty"


def test_parse_username_without_at():
    kind, value = parse_user_search_query("buriev2")
    assert kind == "username"
    assert value == "buriev2"
