from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_image_model: str = Field(default="gpt-image-1", alias="OPENAI_IMAGE_MODEL")
    openai_image_model_fallbacks: str = Field(
        default="dall-e-2",
        alias="OPENAI_IMAGE_MODEL_FALLBACKS",
    )
    advanced_openai_model: str = Field(default="gpt-5.4-mini", alias="ADVANCED_OPENAI_MODEL")
    pro_openai_model: str = Field(default="gpt-5.5", alias="PRO_OPENAI_MODEL")
    premium_openai_model: str = Field(default="", alias="PREMIUM_OPENAI_MODEL")
    payment_contact: str = Field(default="", alias="PAYMENT_CONTACT")
    payment_card_number: str = Field(default="", alias="PAYMENT_CARD_NUMBER")
    payment_card_holder: str = Field(default="", alias="PAYMENT_CARD_HOLDER")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./life_ai.db",
        alias="DATABASE_URL",
    )
    default_language: str = Field(default="ru", alias="DEFAULT_LANGUAGE")
    default_passport_country: str = Field(default="Узбекистан", alias="DEFAULT_PASSPORT_COUNTRY")
    webhook_url: str = Field(default="", alias="WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    webhook_host: str = Field(default="0.0.0.0", alias="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, alias="WEBHOOK_PORT")
    admin_telegram_ids: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")
    admin_new_user_notify: bool = Field(default=True, alias="ADMIN_NEW_USER_NOTIFY")
    admin_ai_request_notify: bool = Field(default=True, alias="ADMIN_AI_REQUEST_NOTIFY")
    web_search_enabled: bool = Field(default=True, alias="WEB_SEARCH_ENABLED")
    web_search_all_modules: bool = Field(default=True, alias="WEB_SEARCH_ALL_MODULES")
    web_search_force_required: bool = Field(default=True, alias="WEB_SEARCH_FORCE_REQUIRED")
    web_search_context_size: str = Field(default="high", alias="WEB_SEARCH_CONTEXT_SIZE")
    web_search_unlimited_context: bool = Field(default=True, alias="WEB_SEARCH_UNLIMITED_CONTEXT")
    web_search_max_results: int = Field(default=15, alias="WEB_SEARCH_MAX_RESULTS")
    web_search_max_queries: int = Field(default=6, alias="WEB_SEARCH_MAX_QUERIES")
    web_search_max_links_footer: int = Field(default=20, alias="WEB_SEARCH_MAX_LINKS_FOOTER")
    web_search_timeout_seconds: float = Field(default=20.0, alias="WEB_SEARCH_TIMEOUT_SECONDS")

    @property
    def admin_telegram_id_list(self) -> list[int]:
        from app.services.admin_service import parse_admin_telegram_ids

        return parse_admin_telegram_ids(self.admin_telegram_ids)


    @property
    def effective_advanced_model(self) -> str:
        advanced = self.advanced_openai_model.strip()
        if advanced:
            return advanced
        legacy = self.premium_openai_model.strip()
        return legacy or "gpt-5.4-mini"


    @property
    def effective_pro_model(self) -> str:
        pro = self.pro_openai_model.strip()
        if pro:
            return pro
        legacy = self.premium_openai_model.strip()
        if legacy and legacy not in (self.openai_model, self.advanced_openai_model):
            return legacy
        return "gpt-5.5"


settings = Settings()
