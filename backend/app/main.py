import logging

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import OutfitRecommendation, RecommendationRequest, WeatherSnapshot
from app.services.llm import check_gemini_key_status, generate_llm_recommendation
from app.services.rules import generate_rule_based_recommendation
from app.services.weather import fetch_weather_snapshot

app = FastAPI(title="Weather Wear API", version="0.1.0")
logger = logging.getLogger("uvicorn.error")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def validate_gemini_on_startup() -> None:
    is_valid, message = await check_gemini_key_status()
    if is_valid:
        logger.info(message)
    else:
        logger.warning(message)


@app.get("/api/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/api/weather", response_model=WeatherSnapshot)
async def get_weather(query: str = Query(..., min_length=2)) -> WeatherSnapshot:
    return await fetch_weather_snapshot(query)


@app.post("/api/recommend", response_model=OutfitRecommendation)
async def recommend_outfit(payload: RecommendationRequest) -> OutfitRecommendation:
    baseline = generate_rule_based_recommendation(payload.weather, payload.preferences)
    llm_recommendation = await generate_llm_recommendation(
        payload.weather, payload.preferences, baseline
    )
    if llm_recommendation:
        return llm_recommendation
    return baseline
