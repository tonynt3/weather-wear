import { useMemo, useState } from "react";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

const initialPreferences = {
  cold_sensitivity: "medium",
  style: "casual",
  activity_level: "medium",
  carry_umbrella: true
};

function App() {
  const [query, setQuery] = useState("Atlanta");
  const [weather, setWeather] = useState(null);
  const [recommendation, setRecommendation] = useState(null);
  const [preferences, setPreferences] = useState(initialPreferences);
  const [loadingWeather, setLoadingWeather] = useState(false);
  const [loadingRecommendation, setLoadingRecommendation] = useState(false);
  const [error, setError] = useState("");

  const canRecommend = useMemo(() => Boolean(weather), [weather]);
  const weatherMetrics = weather
    ? [
        { label: "Location", value: weather.location },
        { label: "Temperature", value: `${weather.temperature_f}F` },
        { label: "Feels Like", value: `${weather.feels_like_f}F` },
        { label: "Condition", value: weather.condition },
        {
          label: "Precipitation",
          value: `${weather.precipitation_probability}% chance`
        },
        { label: "Wind", value: `${weather.wind_mph} mph` },
        { label: "UV Index", value: `${weather.uv_index}` }
      ]
    : [];

  const fetchWeather = async (event) => {
    event.preventDefault();
    setError("");
    setRecommendation(null);
    setLoadingWeather(true);

    try {
      const response = await fetch(
        `${API_BASE_URL}/api/weather?query=${encodeURIComponent(query)}`
      );
      if (!response.ok) {
        throw new Error(`Weather request failed (${response.status})`);
      }
      const data = await response.json();
      setWeather(data);
    } catch (requestError) {
      setError(requestError.message);
      setWeather(null);
    } finally {
      setLoadingWeather(false);
    }
  };

  const fetchRecommendation = async () => {
    if (!weather) {
      return;
    }

    setError("");
    setLoadingRecommendation(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/recommend`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          weather,
          preferences
        })
      });

      if (!response.ok) {
        throw new Error(`Recommendation request failed (${response.status})`);
      }

      const data = await response.json();
      setRecommendation(data);
    } catch (requestError) {
      setError(requestError.message);
      setRecommendation(null);
    } finally {
      setLoadingRecommendation(false);
    }
  };

  return (
    <main className="app-shell">
      <header className="hero">
        <p className="eyebrow">Smart Daily Outfit Planner</p>
        <h1>Weather Wear</h1>
        <p className="subtitle">
          Get weather-aware recommendations with reliable rules and optional LLM
          personalization.
        </p>
      </header>

      <section className="card">
        <h2>Preferences</h2>

        <form onSubmit={fetchWeather} className="form-grid">
          <label className="field location-field">
            Location
            <input
              type="text"
              value={query}
              onChange={(event) => setQuery(event.target.value)}
              placeholder="City or place name"
              required
            />
          </label>

          <label className="field">
            Style
            <select
              value={preferences.style}
              onChange={(event) =>
                setPreferences((prev) => ({ ...prev, style: event.target.value }))
              }
            >
              <option value="casual">Casual</option>
              <option value="athleisure">Athleisure</option>
              <option value="business_casual">Business Casual</option>
            </select>
          </label>

          <label className="field">
            Cold Sensitivity
            <select
              value={preferences.cold_sensitivity}
              onChange={(event) =>
                setPreferences((prev) => ({
                  ...prev,
                  cold_sensitivity: event.target.value
                }))
              }
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>

          <label className="field">
            Activity Level
            <select
              value={preferences.activity_level}
              onChange={(event) =>
                setPreferences((prev) => ({
                  ...prev,
                  activity_level: event.target.value
                }))
              }
            >
              <option value="low">Low</option>
              <option value="medium">Medium</option>
              <option value="high">High</option>
            </select>
          </label>

          <label className="field checkbox">
            <input
              type="checkbox"
              checked={preferences.carry_umbrella}
              onChange={(event) =>
                setPreferences((prev) => ({
                  ...prev,
                  carry_umbrella: event.target.checked
                }))
              }
            />
            Carry umbrella when needed
          </label>

          <div className="button-row">
            <button type="submit" disabled={loadingWeather}>
              {loadingWeather ? "Loading weather..." : "Fetch Weather"}
            </button>
            <button
              type="button"
              onClick={fetchRecommendation}
              disabled={!canRecommend || loadingRecommendation}
              className="secondary"
            >
              {loadingRecommendation ? "Generating..." : "Get Outfit Recommendation"}
            </button>
          </div>
        </form>

        {error && <p className="error">{error}</p>}
      </section>

      {weather && (
        <section className="card">
          <h2>Current Weather</h2>
          <div className="metric-grid">
            {weatherMetrics.map((metric) => (
              <article className="metric-card" key={metric.label}>
                <p className="metric-label">{metric.label}</p>
                <p className="metric-value">{metric.value}</p>
              </article>
            ))}
          </div>
        </section>
      )}

      {recommendation && (
        <section className="card">
          <div className="recommendation-header">
            <h2>Outfit Recommendation</h2>
            <span className={`source-pill ${recommendation.source}`}>
              {recommendation.source === "llm" ? "LLM enhanced" : "Rule based"}
            </span>
          </div>

          <div className="outfit-grid">
            <article className="outfit-item">
              <p className="metric-label">Top</p>
              <p className="metric-value">{recommendation.top}</p>
            </article>
            <article className="outfit-item">
              <p className="metric-label">Bottom</p>
              <p className="metric-value">{recommendation.bottom}</p>
            </article>
            <article className="outfit-item">
              <p className="metric-label">Outerwear</p>
              <p className="metric-value">{recommendation.outerwear}</p>
            </article>
            <article className="outfit-item">
              <p className="metric-label">Footwear</p>
              <p className="metric-value">{recommendation.footwear}</p>
            </article>
          </div>

          <div className="details-row">
            <p>
              <strong>Confidence:</strong> {recommendation.confidence}
            </p>
            <div className="accessory-list">
              {recommendation.accessories.length ? (
                recommendation.accessories.map((item) => (
                  <span key={item} className="chip">
                    {item}
                  </span>
                ))
              ) : (
                <span className="chip muted">No accessories needed</span>
              )}
            </div>
          </div>

          <p className="rationale">{recommendation.rationale}</p>
        </section>
      )}
    </main>
  );
}

export default App;
