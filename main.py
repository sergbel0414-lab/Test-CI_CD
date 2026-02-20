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

WEEKDAYS_RU = [
    "понедельник",
    "вторник",
    "среда",
    "четверг",
    "пятница",
    "суббота",
    "воскресенье",
]

MONTHS_RU = [
    "января",
    "февраля",
    "марта",
    "апреля",
    "мая",
    "июня",
    "июля",
    "августа",
    "сентября",
    "октября",
    "ноября",
    "декабря",
]


def pluralize_ru(value: int, one: str, few: str, many: str) -> str:
    last_two = value % 100
    last_one = value % 10

    if 11 <= last_two <= 14:
        return many
    if last_one == 1:
        return one
    if 2 <= last_one <= 4:
        return few
    return many


@app.get("/")
def healthcheck() -> dict[str, str]:
    return {
        "status": "ok",
        "message": (
            "Use /time/{city}, /date/{city}, /datetime-in-words/{city}, "
            "or /convert-timezone to work with time."
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


@app.get("/datetime-in-words/{city}")
def get_city_datetime_in_words(city: str) -> dict[str, str]:
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

    current_dt = datetime.now(ZoneInfo(timezone_name))
    weekday_text = WEEKDAYS_RU[current_dt.weekday()]
    month_text = MONTHS_RU[current_dt.month - 1]

    hour_word = pluralize_ru(current_dt.hour, "час", "часа", "часов")
    minute_word = pluralize_ru(current_dt.minute, "минута", "минуты", "минут")
    second_word = pluralize_ru(current_dt.second, "секунда", "секунды", "секунд")

    datetime_text = (
        f"{weekday_text}, {current_dt.day} {month_text} {current_dt.year} года, "
        f"{current_dt.hour} {hour_word} {current_dt.minute} {minute_word} "
        f"{current_dt.second} {second_word}"
    )

    return {
        "city": city,
        "timezone": timezone_name,
        "datetime_in_words": datetime_text,
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
