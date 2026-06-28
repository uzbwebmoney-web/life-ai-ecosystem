from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bot_token: str = Field(alias="BOT_TOKEN")
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    premium_openai_model: str = Field(default="gpt-4o", alias="PREMIUM_OPENAI_MODEL")
    payment_contact: str = Field(default="", alias="PAYMENT_CONTACT")
    payment_card_number: str = Field(default="", alias="PAYMENT_CARD_NUMBER")
    payment_card_holder: str = Field(default="", alias="PAYMENT_CARD_HOLDER")
    database_url: str = Field(
        default="sqlite+aiosqlite:///./life_ai.db",
        alias="DATABASE_URL",
    )
    default_language: str = Field(default="ru", alias="DEFAULT_LANGUAGE")
    webhook_url: str = Field(default="", alias="WEBHOOK_URL")
    webhook_path: str = Field(default="/webhook", alias="WEBHOOK_PATH")
    webhook_host: str = Field(default="0.0.0.0", alias="WEBHOOK_HOST")
    webhook_port: int = Field(default=8080, alias="WEBHOOK_PORT")
    admin_telegram_ids: str = Field(default="", alias="ADMIN_TELEGRAM_IDS")

    @property
    def admin_telegram_id_list(self) -> list[int]:
        from app.services.admin_service import parse_admin_telegram_ids

        return parse_admin_telegram_ids(self.admin_telegram_ids)


settings = Settings()
