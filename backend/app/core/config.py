from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Open Banking Personal Finance AI"
    app_env: str = "local"

    database_url: str = "postgresql+psycopg2://pfai:pfai@db:5432/pfai"

    secret_key: str = "change-this-secret-key"
    algorithm: str = "HS256"

    access_token_expire_minutes: int = 15
    refresh_token_expire_days: int = 30

    cors_origins: str = "http://localhost:3000,http://localhost:3002"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()