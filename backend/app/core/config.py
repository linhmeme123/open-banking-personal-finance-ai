from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env")

    app_env: str = "local"
    database_url: str = "postgresql+psycopg2://pfai:pfai@localhost:55432/pfai"
    cors_origins: str = "http://localhost:3000"
    secret_key: str = "dev-secret-change-me"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
