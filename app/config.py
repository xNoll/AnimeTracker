from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    database_url: str    # default - SQLite for local dev

    # External API
    jikan_api_url: str

    # App
    app_name: str = "AnimeTracker API"
    debug: bool = True

    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instanciated only once and used wherever imported.
settings = Settings()
