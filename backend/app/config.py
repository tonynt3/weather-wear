from typing import Optional

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    gemini_api_key: Optional[str] = None
    gemini_model: str = "gemini-2.5-flash"
    frontend_origin: str = "http://localhost:5173"
    weather_api_base_url: str = "https://api.open-meteo.com/v1/forecast"
    geocoding_api_base_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    request_timeout_seconds: float = 10.0

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @field_validator("gemini_api_key")
    @classmethod
    def normalize_empty_value(cls, value: Optional[str]) -> Optional[str]:
        if value and value.strip():
            return value.strip()
        return None


settings = Settings()
