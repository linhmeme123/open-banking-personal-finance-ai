from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Open Banking Personal Finance AI"

    database_url: str = "postgresql+psycopg2://pfai:pfai@localhost:55432/pfai"

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


settings = Settings()