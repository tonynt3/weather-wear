# Weather Wear MVP

Starter project with:
- `frontend/`: React (Vite) UI
- `backend/`: FastAPI service for weather + outfit recommendation

The backend fetches live weather from Open-Meteo, generates a deterministic rule-based outfit, then optionally asks Gemini to personalize the response.

## 1) Backend setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

Optional: add `GEMINI_API_KEY` in `backend/.env` to enable LLM recommendations.  
Without it, recommendations still work using the rule engine.

## 2) Frontend setup

```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```

Frontend default URL: `http://localhost:5173`  
Backend default URL: `http://localhost:8000`

## API endpoints

- `GET /api/health`
- `GET /api/weather?query=<location>`
- `POST /api/recommend`

`POST /api/recommend` request body:

```json
{
  "weather": {
    "location": "San Francisco, California, United States",
    "temperature_f": 62.1,
    "feels_like_f": 61.3,
    "wind_mph": 8.5,
    "precipitation_probability": 10,
    "uv_index": 4.2,
    "condition": "Partly cloudy"
  },
  "preferences": {
    "cold_sensitivity": "medium",
    "style": "casual",
    "activity_level": "medium",
    "carry_umbrella": true
  }
}
```

## Notes for next iteration

- Add a persistent user profile table (style + sensitivity + feedback).
- Add retry/caching for weather API responses.
- Add unit tests for rules and response schema validation.
