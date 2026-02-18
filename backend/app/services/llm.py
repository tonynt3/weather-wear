import asyncio
import json
from typing import Optional, Tuple

from google import genai
from google.genai import types

from app.config import settings
from app.models import OutfitRecommendation, UserPreferences, WeatherSnapshot


SYSTEM_PROMPT = (
    "You are a weather stylist assistant. Return only valid JSON with keys: "
    "top, bottom, outerwear, footwear, accessories, rationale, confidence. "
    "Do not include markdown or extra text."
)

RECOMMENDATION_JSON_SCHEMA = {
    "type": "object",
    "required": [
        "top",
        "bottom",
        "outerwear",
        "footwear",
        "accessories",
        "rationale",
        "confidence",
    ],
    "properties": {
        "top": {"type": "string"},
        "bottom": {"type": "string"},
        "outerwear": {"type": "string"},
        "footwear": {"type": "string"},
        "accessories": {"type": "array", "items": {"type": "string"}},
        "rationale": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "additionalProperties": False,
}


def _extract_json(text: str) -> dict:
    candidate = text.strip()
    if candidate.startswith("```"):
        lines = candidate.splitlines()
        if len(lines) >= 3:
            candidate = "\n".join(lines[1:-1]).strip()

    start = candidate.find("{")
    end = candidate.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("No JSON object found in model output.")

    return json.loads(candidate[start : end + 1])


def _build_user_prompt(
    weather: WeatherSnapshot, preferences: UserPreferences, baseline: OutfitRecommendation
) -> str:
    return (
        f"Weather: {weather.model_dump_json()}\n"
        f"Preferences: {preferences.model_dump_json()}\n"
        f"Baseline recommendation: {baseline.model_dump_json()}\n"
        "Generate a concise outfit recommendation tuned to the user preferences.\n"
        "Rules:\n"
        "- Confidence must be a number between 0 and 1.\n"
        "- Accessories must be an array of strings.\n"
        "- Keep rationale to one sentence.\n"
    )


def _masked_key(value: str) -> str:
    if len(value) <= 8:
        return "*" * len(value)
    return f"{value[:4]}...{value[-4:]}"


async def check_gemini_key_status() -> Tuple[bool, str]:
    if not settings.gemini_api_key:
        return (
            False,
            "Gemini disabled: GEMINI_API_KEY is not set. Recommendations will use rule-based fallback.",
        )

    client = genai.Client(api_key=settings.gemini_api_key)
    masked = _masked_key(settings.gemini_api_key)

    try:
        await asyncio.wait_for(
            asyncio.to_thread(
                client.models.generate_content,
                model=settings.gemini_model,
                contents="Reply with OK.",
                config=types.GenerateContentConfig(
                    temperature=0,
                    max_output_tokens=8,
                ),
            ),
            timeout=settings.request_timeout_seconds + 2,
        )
        return (
            True,
            f"Gemini enabled: API key {masked} validated for model '{settings.gemini_model}'.",
        )
    except Exception as exc:
        return (
            False,
            "Gemini key/model check failed for "
            f"'{settings.gemini_model}' with key {masked}: {exc.__class__.__name__}: {exc}",
        )


async def generate_llm_recommendation(
    weather: WeatherSnapshot, preferences: UserPreferences, baseline: OutfitRecommendation
) -> Optional[OutfitRecommendation]:
    if not settings.gemini_api_key:
        return None

    client = genai.Client(api_key=settings.gemini_api_key)
    user_prompt = _build_user_prompt(weather, preferences, baseline)

    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=settings.gemini_model,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                temperature=0.2,
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_json_schema=RECOMMENDATION_JSON_SCHEMA,
            ),
        )
        raw_text = response.text or ""
        parsed = _extract_json(raw_text)
        parsed["source"] = "llm"
        return OutfitRecommendation.model_validate(parsed)
    except Exception:
        return None
