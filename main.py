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
    return {
        "status": "ok",
        "message": (
            "Use /time/{city}, /date/{city}, or /convert-timezone to work with time."
        ),
    }


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


@app.get("/date/{city}")
def get_city_date(city: str) -> dict[str, str]:
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

    current_date = datetime.now(ZoneInfo(timezone_name)).date()
    return {
        "city": city,
        "timezone": timezone_name,
        "current_date": current_date.isoformat(),
    }


@app.get("/convert-timezone")
def convert_timezone(
    current_time: str,
    from_timezone: str,
    to_timezone: str,
) -> dict[str, str]:
    try:
        source_tz = ZoneInfo(from_timezone)
        target_tz = ZoneInfo(to_timezone)
    except Exception as exc:
        raise HTTPException(
            status_code=400,
            detail="Invalid timezone. Example: Europe/Moscow, America/New_York.",
        ) from exc

    try:
        parsed_time = datetime.fromisoformat(current_time)
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid time format. Use ISO format, for example: "
                "2026-02-19T15:30:00"
            ),
        ) from exc

    # If input datetime has no offset/timezone, we treat it as time in from_timezone.
    if parsed_time.tzinfo is None:
        parsed_time = parsed_time.replace(tzinfo=source_tz)
    else:
        parsed_time = parsed_time.astimezone(source_tz)

    converted = parsed_time.astimezone(target_tz)

    return {
        "source_time": parsed_time.isoformat(),
        "source_timezone": from_timezone,
        "target_timezone": to_timezone,
        "converted_time": converted.isoformat(),
    }
