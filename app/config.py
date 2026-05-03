from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    database_url: str = "sqlite:///./gallery.db"
    secret_key: str = "dev_secret_key_change_in_production_12345"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 15
    app_name: str = "Internet Gallery API"
    
    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()