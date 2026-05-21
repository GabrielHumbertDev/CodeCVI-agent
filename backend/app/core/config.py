from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # AI Service
    ai_service_url: str = "http://localhost:8001"
    ai_provider: str = "local"
    ollama_model: str = "qwen2.5:7b"
    ollama_url: str = "http://localhost:11434"
    anthropic_api_key: str = ""

    # Embeddings
    embedding_model: str = "nomic-embed-text"
    embedding_dim: int = 768

    # App
    app_name: str = "CV Platform API"
    debug: bool = False
    backend_cors_origins: str = "http://localhost:3000"

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
