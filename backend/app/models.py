from typing import Literal

from pydantic import BaseModel, Field


class WeatherSnapshot(BaseModel):
    location: str
    temperature_f: float
    feels_like_f: float
    wind_mph: float
    precipitation_probability: int = Field(ge=0, le=100)
    uv_index: float
    condition: str


class UserPreferences(BaseModel):
    cold_sensitivity: Literal["low", "medium", "high"] = "medium"
    style: Literal["casual", "athleisure", "business_casual"] = "casual"
    activity_level: Literal["low", "medium", "high"] = "medium"
    carry_umbrella: bool = True


class RecommendationRequest(BaseModel):
    weather: WeatherSnapshot
    preferences: UserPreferences = UserPreferences()


class OutfitRecommendation(BaseModel):
    top: str
    bottom: str
    outerwear: str
    footwear: str
    accessories: list[str] = Field(default_factory=list)
    rationale: str
    confidence: float = Field(ge=0, le=1)
    source: Literal["llm", "rules"]

