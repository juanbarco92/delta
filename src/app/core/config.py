from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://user:password@localhost:5433/delta_db"
    
    # Mercado Libre Params (from previous context, usually good to keep here too)
    MELI_client_id: str = ""
    MELI_client_secret: str = ""
    MELI_redirect_uri: str = ""

    model_config = SettingsConfigDict(env_file=".env", env_ignore_empty=True, extra="ignore")

settings = Settings()
