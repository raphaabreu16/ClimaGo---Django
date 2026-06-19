import requests


def get_coordinates(city_name):
    geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"

    params = {
        "name": city_name,
        "count": 1,
        "language": "pt",
        "format": "json",
    }

    response = requests.get(geocoding_url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    if "results" not in data or not data["results"]:
        return None

    location = data["results"][0]

    return {
        "city": location["name"],
        "country": location.get("country", ""),
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "timezone": location.get("timezone", "America/Sao_Paulo"),
    }


def get_weather(city_name="Rio de Janeiro"):
    location = get_coordinates(city_name)

    if location is None:
        return {
            "city": city_name,
            "temperature": "--",
            "humidity": "--",
            "wind_speed": "--",
            "weather_code": None,
            "forecast": [],
        }

    forecast_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": location["timezone"],
        "forecast_days": 7,
    }

    response = requests.get(forecast_url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()
    current = data["current"]
    daily = data["daily"]

    return {
        "city": location["city"],
        "country": location["country"],
        "temperature": round(current["temperature_2m"]),
        "humidity": current["relative_humidity_2m"],
        "wind_speed": round(current["wind_speed_10m"]),
        "weather_code": current["weather_code"],
        "forecast": format_forecast(daily),
    }


def format_forecast(daily):
    forecast = []

    for index, date in enumerate(daily["time"]):
        forecast.append(
            {
                "date": date,
                "max_temp": round(daily["temperature_2m_max"][index]),
                "min_temp": round(daily["temperature_2m_min"][index]),
                "rain_chance": daily["precipitation_probability_max"][index],
            }
        )

    return forecast