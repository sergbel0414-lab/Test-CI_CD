from datetime import datetime
from zoneinfo import ZoneInfo

from fastapi import FastAPI, HTTPException

app = FastAPI(title="City Time API", version="1.0.0")

# Небольшой словарь тестовых городов и соответствующих часовых поясов.
CITY_TIMEZONES = {
    "moscow": "Europe/Moscow",
    "москва": "Europe/Moscow",
    "london": "Europe/London",
    "лондон": "Europe/London",
    "new york": "America/New_York",
    "нью-йорк": "America/New_York",
    "tokyo": "Asia/Tokyo",
    "токио": "Asia/Tokyo",
}


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {"status": "ok", "message": "Use /time/{city} to get city time."}


@app.get("/time/{city}")
def get_city_time(city: str) -> dict[str, str]:
    normalized_city = city.strip().lower()
    timezone_name = CITY_TIMEZONES.get(normalized_city)

    if timezone_name is None:
        raise HTTPException(
            status_code=404,
            detail=(
                f"City '{city}' is not supported. "
                "Try: Moscow, London, New York, Tokyo."
            ),
        )

    current_time = datetime.now(ZoneInfo(timezone_name))
    return {
        "city": city,
        "timezone": timezone_name,
        "current_time": current_time.isoformat(),
    }
