from pydantic_settings import BaseSettings
from functools import lru_cache
from pathlib import Path
import os

# Always resolve .env relative to this file, regardless of CWD
_ENV_FILE = Path(__file__).resolve().parent.parent / ".env"
print(f"[CONFIG] Looking for .env at: {_ENV_FILE}")
print(f"[CONFIG] .env exists: {_ENV_FILE.exists()}")
print(f"[CONFIG] Current working directory: {os.getcwd()}")


class Settings(BaseSettings):
    app_name: str = "SimplifyAI"
    debug: bool = False

    # AI Provider
    ai_provider: str = "groq"
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"
    google_api_key: str = ""
    gemini_model: str = "gemini-2.5-flash"
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"

    # Database
    database_url: str = "sqlite:///./simplifyai.db"

    # Upload size limit in MB
    max_upload_size_mb: int = 10

    class Config:
        env_file = str(_ENV_FILE)
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    s = Settings()
    key = s.groq_api_key
    masked = (key[:6] + "..." + key[-4:]) if len(key) > 10 else f"(empty or too short: len={len(key)})"
    print(f"[CONFIG] ai_provider  = {s.ai_provider}")
    print(f"[CONFIG] groq_model   = {s.groq_model}")
    print(f"[CONFIG] groq_api_key = {masked}")
    return s
