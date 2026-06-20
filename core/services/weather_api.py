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
    today_rain_chance = daily["precipitation_probability_max"][0]
today_max_temp = daily["temperature_2m_max"][0]
today_min_temp = daily["temperature_2m_min"][0]

score = calculate_climago_score(
    temperature=current["temperature_2m"],
    humidity=current["relative_humidity_2m"],
    wind_speed=current["wind_speed_10m"],
    rain_chance=today_rain_chance,
    temp_max=today_max_temp,
    temp_min=today_min_temp,
    weather_code=current["weather_code"],
)

    return {
        "city": location["city"],
        "country": location["country"],
        "temperature": round(current["temperature_2m"]),
        "humidity": current["relative_humidity_2m"],
        "wind_speed": round(current["wind_speed_10m"]),
        "weather_code": current["weather_code"],
        "forecast": format_forecast(daily),
        "score": score,
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
    
def calculate_climago_score(
    temperature,
    humidity,
    wind_speed,
    rain_chance,
    uv_index=None,
    temp_max=None,
    temp_min=None,
    weather_code=None,
):
    score = 100

    # 1. Temperatura
    # Faixa confortável: 18°C a 30°C
    if temperature >= 38:
        score -= 25
    elif temperature >= 34:
        score -= 18
    elif temperature >= 31:
        score -= 10
    elif temperature < 10:
        score -= 20
    elif temperature < 15:
        score -= 12
    elif temperature < 18:
        score -= 5

    # 2. Umidade
    # Umidade muito alta deixa o clima abafado; muito baixa pode ser desconfortável
    if humidity >= 90:
        score -= 15
    elif humidity >= 80:
        score -= 10
    elif humidity >= 70:
        score -= 5
    elif humidity <= 25:
        score -= 8

    # 3. Vento
    if wind_speed >= 45:
        score -= 25
    elif wind_speed >= 35:
        score -= 18
    elif wind_speed >= 25:
        score -= 10
    elif wind_speed >= 18:
        score -= 5

    # 4. Chance de chuva
    if rain_chance >= 80:
        score -= 30
    elif rain_chance >= 60:
        score -= 22
    elif rain_chance >= 40:
        score -= 15
    elif rain_chance >= 20:
        score -= 7

    # 5. Índice UV
    # Só aplica se a API estiver trazendo esse dado
    if uv_index is not None:
        if uv_index >= 11:
            score -= 15
        elif uv_index >= 8:
            score -= 10
        elif uv_index >= 6:
            score -= 5

    # 6. Amplitude térmica
    # Diferença muito grande entre máxima e mínima pode indicar instabilidade
    if temp_max is not None and temp_min is not None:
        thermal_range = temp_max - temp_min

        if thermal_range >= 15:
            score -= 10
        elif thermal_range >= 10:
            score -= 5

    # 7. Código climático
    # Penaliza chuva forte, tempestade, neblina etc.
    if weather_code is not None:
        if weather_code in [95, 96, 99]:
            score -= 25
        elif weather_code in [65, 66, 67, 80, 81, 82]:
            score -= 20
        elif weather_code in [61, 63]:
            score -= 12
        elif weather_code in [45, 48]:
            score -= 8
        elif weather_code in [0, 1]:
            score += 3

    return max(min(round(score), 100), 0)