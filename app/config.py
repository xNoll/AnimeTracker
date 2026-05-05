from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./animetracker.db"   # default - SQLite for local dev

    # External API
    jikan_api_url: str = "https://api.jikan.moe/v4"

    # App
    app_name: str = "AnimeTracker API"
    debug: bool = True

    secret_key: str

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

# Instanciated only once and used wherever imported.
settings = Settings()
