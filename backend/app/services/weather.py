from fastapi import HTTPException
import httpx

from app.config import settings
from app.models import WeatherSnapshot

WEATHER_CODE_MAP = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Rain showers",
    81: "Rain showers",
    82: "Heavy rain showers",
    85: "Snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with hail",
    99: "Thunderstorm with hail",
}


def c_to_f(celsius: float) -> float:
    return (celsius * 9 / 5) + 32


def kmh_to_mph(kmh: float) -> float:
    return kmh * 0.621371


async def geocode_location(query: str) -> dict:
    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(
            settings.geocoding_api_base_url,
            params={"name": query, "count": 1, "language": "en", "format": "json"},
        )
        response.raise_for_status()

    payload = response.json()
    results = payload.get("results", [])
    if not results:
        raise HTTPException(status_code=404, detail=f"Location not found: {query}")

    top = results[0]
    display_name = ", ".join(
        part for part in [top.get("name"), top.get("admin1"), top.get("country")] if part
    )

    return {
        "latitude": top["latitude"],
        "longitude": top["longitude"],
        "display_name": display_name,
    }


async def fetch_weather_snapshot(query: str) -> WeatherSnapshot:
    location = await geocode_location(query)

    async with httpx.AsyncClient(timeout=settings.request_timeout_seconds) as client:
        response = await client.get(
            settings.weather_api_base_url,
            params={
                "latitude": location["latitude"],
                "longitude": location["longitude"],
                "current": ",".join(
                    [
                        "temperature_2m",
                        "apparent_temperature",
                        "precipitation_probability",
                        "weather_code",
                        "wind_speed_10m",
                        "uv_index",
                    ]
                ),
                "timezone": "auto",
                "temperature_unit": "celsius",
                "wind_speed_unit": "kmh",
            },
        )
        response.raise_for_status()

    payload = response.json()
    current = payload.get("current")
    if not current:
        raise HTTPException(status_code=502, detail="Weather provider returned no current data.")

    weather_code = int(current.get("weather_code", -1))

    return WeatherSnapshot(
        location=location["display_name"],
        temperature_f=round(c_to_f(float(current.get("temperature_2m", 0.0))), 1),
        feels_like_f=round(c_to_f(float(current.get("apparent_temperature", 0.0))), 1),
        wind_mph=round(kmh_to_mph(float(current.get("wind_speed_10m", 0.0))), 1),
        precipitation_probability=int(round(float(current.get("precipitation_probability") or 0))),
        uv_index=round(float(current.get("uv_index") or 0.0), 1),
        condition=WEATHER_CODE_MAP.get(weather_code, "Unknown conditions"),
    )

