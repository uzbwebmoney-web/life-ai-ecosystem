from app.core.i18n import t


def test_support_i18n_keys_exist():
    for lang in ("ru", "uz", "en"):
        assert t(lang, "btn_contact_admin")
        assert t(lang, "support_intro")
        assert t(lang, "support_sent")
