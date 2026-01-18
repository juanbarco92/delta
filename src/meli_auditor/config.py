from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ID: str
    CLIENT_SECRET: str
    REDIRECT_URI: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()
