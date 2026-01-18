from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8', extra="ignore")

settings = Settings()
