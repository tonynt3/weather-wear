from app.models import OutfitRecommendation, UserPreferences, WeatherSnapshot


def generate_rule_based_recommendation(
    weather: WeatherSnapshot, preferences: UserPreferences
) -> OutfitRecommendation:
    feels_like = weather.feels_like_f
    precip = weather.precipitation_probability

    top = "T-shirt"
    bottom = "Jeans"
    outerwear = "No extra layer"
    footwear = "Sneakers"
    accessories: list[str] = []

    if feels_like < 32:
        top = "Thermal base layer + sweater"
        bottom = "Insulated pants"
        outerwear = "Heavy winter coat"
        footwear = "Waterproof boots"
        accessories.extend(["Gloves", "Beanie"])
    elif feels_like < 45:
        top = "Long-sleeve shirt + sweater"
        bottom = "Jeans"
        outerwear = "Warm jacket"
        footwear = "Boots"
    elif feels_like < 60:
        top = "Long-sleeve shirt"
        bottom = "Jeans or chinos"
        outerwear = "Light jacket"
        footwear = "Sneakers"
    elif feels_like < 75:
        top = "Breathable shirt"
        bottom = "Chinos or jeans"
        outerwear = "Optional overshirt"
        footwear = "Sneakers"
    elif feels_like < 88:
        top = "Lightweight T-shirt"
        bottom = "Shorts or light pants"
        outerwear = "No outerwear"
        footwear = "Breathable sneakers"
    else:
        top = "Moisture-wicking tee"
        bottom = "Shorts"
        outerwear = "No outerwear"
        footwear = "Ventilated shoes"
        accessories.append("Water bottle")

    if precip >= 50:
        if preferences.carry_umbrella:
            accessories.append("Umbrella")
        outerwear = "Rain jacket"
        footwear = "Water-resistant shoes"

    if weather.wind_mph >= 20:
        accessories.append("Windproof layer")

    if weather.uv_index >= 6:
        accessories.extend(["Sunglasses", "SPF 30+ sunscreen"])

    if preferences.style == "business_casual":
        top = "Collared shirt"
        if feels_like < 60:
            outerwear = "Structured coat or blazer"
        bottom = "Chinos or slacks"
        footwear = "Loafers or leather sneakers"
    elif preferences.style == "athleisure":
        top = "Performance top"
        bottom = "Joggers" if feels_like < 75 else "Athletic shorts"
        footwear = "Running shoes"

    if preferences.cold_sensitivity == "high" and feels_like < 70 and "Light jacket" in outerwear:
        outerwear = "Midweight jacket"
    elif preferences.cold_sensitivity == "low" and feels_like >= 55:
        outerwear = "No extra layer"

    rationale = (
        f"Feels like {feels_like:.1f}F with {precip}% precipitation chance. "
        f"Condition: {weather.condition}. Recommendation tuned for {preferences.style} style."
    )

    confidence = 0.72
    if precip >= 50 or feels_like <= 35 or feels_like >= 90:
        confidence += 0.08
    if weather.condition.lower().startswith("unknown"):
        confidence -= 0.1

    return OutfitRecommendation(
        top=top,
        bottom=bottom,
        outerwear=outerwear,
        footwear=footwear,
        accessories=sorted(set(accessories)),
        rationale=rationale,
        confidence=round(max(min(confidence, 0.95), 0.4), 2),
        source="rules",
    )

