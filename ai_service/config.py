from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    ollama_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5:7b"
    request_timeout: int = 120  # seconds
    max_retries: int = 2

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
