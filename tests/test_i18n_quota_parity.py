from app.core.i18n import t


def test_uz_quota_strings_resolve():
    keys = [
        "quota_voice",
        "quota_music",
        "quota_music_separate",
        "quota_music_monthly",
        "quota_vault_lock",
        "quota_photo_ai",
        "quota_ocr",
        "quota_doc_translate",
        "quota_export",
        "quota_advanced_model",
        "quota_pro_model",
        "quota_ai_credits",
        "quota_image_gen_detail",
        "quota_family_profiles",
        "household_join_full",
        "pay_already_processed",
        "sub_vault_lock_on",
        "sub_gpt54_monthly",
    ]
    for key in keys:
        val = t("uz", key)
        assert val != key, f"Missing uz translation for {key}"
        assert len(val) > 3


def test_quota_strings_resolve_in_all_langs():
    for lang in ("ru", "uz", "en"):
        assert t(lang, "quota_export")
        assert t(lang, "quota_ocr")
        assert t(lang, "quota_vault_lock")
