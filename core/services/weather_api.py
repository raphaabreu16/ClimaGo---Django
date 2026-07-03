import requests
from datetime import datetime


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
        return get_empty_weather(city_name)

    forecast_url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code,surface_pressure",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max",
        "timezone": location["timezone"],
        "forecast_days": 7,
    }

    response = requests.get(forecast_url, params=params, timeout=10)
    response.raise_for_status()

    data = response.json()

    current = data["current"]
    daily = data["daily"]

    temperature = current["temperature_2m"]
    humidity = current["relative_humidity_2m"]
    wind_speed = current["wind_speed_10m"]
    weather_code = current["weather_code"]
    pressure = current.get("surface_pressure")

    today_rain_chance = get_list_value(daily, "precipitation_probability_max", 0, 0)

    if today_rain_chance is None:
        today_rain_chance = 0

    today_max_temp = get_list_value(daily, "temperature_2m_max", 0)
    today_min_temp = get_list_value(daily, "temperature_2m_min", 0)
    today_uv_index = get_list_value(daily, "uv_index_max", 0)

    forecast = format_forecast(daily)

    air_quality = get_air_quality(
        latitude=location["latitude"],
        longitude=location["longitude"],
        timezone=location["timezone"],
    )

    score = calculate_climago_score(
        temperature=temperature,
        humidity=humidity,
        wind_speed=wind_speed,
        rain_chance=today_rain_chance,
        uv_index=today_uv_index,
        temp_max=today_max_temp,
        temp_min=today_min_temp,
        weather_code=weather_code,
    )

    confidence = calculate_confidence(
        rain_chance=today_rain_chance,
        wind_speed=wind_speed,
        humidity=humidity,
        weather_code=weather_code,
    )

    best_window = get_best_window(forecast)
    low_risk_day = get_low_risk_day(forecast)

    main_alert = get_main_alert(
        rain_chance=today_rain_chance,
        wind_speed=wind_speed,
        temperature=temperature,
        uv_index=today_uv_index,
        weather_code=weather_code,
    )

    recommendations = generate_recommendations(
        temperature=temperature,
        humidity=humidity,
        rain_chance=today_rain_chance,
        uv_index=today_uv_index,
        wind_speed=wind_speed,
    )

    disease_risks = calculate_disease_risks(
        temperature=temperature,
        humidity=humidity,
        rain_chance=today_rain_chance,
        air_quality=air_quality,
    )

    suggestion = generate_suggestion(
        today_rain_chance=today_rain_chance,
        uv_index=today_uv_index,
        best_window=best_window,
    )

    return {
        "city": location["city"],
        "country": location["country"],
        "temperature": round(temperature),
        "humidity": humidity,
        "wind_speed": round(wind_speed),
        "weather_code": weather_code,
        "icon": get_weather_icon(weather_code),
        "description": get_weather_description(weather_code),
        "today": {
            "max_temp": round(today_max_temp) if today_max_temp is not None else "--",
            "min_temp": round(today_min_temp) if today_min_temp is not None else "--",
            "rain_chance": today_rain_chance,
        },
        "uv_index": round(today_uv_index) if today_uv_index is not None else "--",
        "uv_label": get_uv_label(today_uv_index),
        "uv_display": get_uv_display(today_uv_index),
        "pressure": {
            "value": round(pressure) if pressure is not None else "--",
            "status": get_pressure_status(pressure),
            "score": get_pressure_score(pressure),
        },
        "air_quality": air_quality,
        "forecast": forecast,
        "score": score,
        "score_status": get_score_status(score),
        "confidence": confidence,
        "best_window": best_window,
        "low_risk_day": low_risk_day,
        "main_alert": main_alert,
        "recommendations": recommendations,
        "disease_risks": disease_risks,
        "suggestion": suggestion,
    }


def get_empty_weather(city_name):
    return {
        "city": city_name,
        "country": "",
        "temperature": "--",
        "humidity": "--",
        "wind_speed": "--",
        "weather_code": None,
        "icon": "🌤️",
        "description": "Clima indisponível",
        "today": {
            "max_temp": "--",
            "min_temp": "--",
            "rain_chance": "--",
        },
        "uv_index": "--",
        "uv_label": "Indisponível",
        "uv_display": "Indisponível",
        "pressure": {
            "value": "--",
            "status": "Indisponível",
            "score": "--",
        },
        "air_quality": {
            "aqi": "--",
            "pm10": "--",
            "pm25": "--",
            "status": "Indisponível",
            "status_class": "",
            "score": "--",
        },
        "forecast": [],
        "score": "--",
        "score_status": "Indisponível",
        "confidence": "--",
        "best_window": {
            "title": "Melhor janela de 5 dias",
            "text": "Não foi possível calcular a melhor janela climática.",
        },
        "low_risk_day": {
            "title": "Menor risco climático",
            "text": "Não foi possível calcular o menor risco climático.",
        },
        "main_alert": {
            "icon": "⚠️",
            "title": "Dados indisponíveis",
            "text": "Não foi possível carregar os alertas climáticos.",
            "card_class": "danger-alert",
        },
        "recommendations": [
            {
                "icon": "ℹ️",
                "title": "Dados indisponíveis",
                "text": "Tente buscar outra cidade ou atualize a página.",
            }
        ],
        "disease_risks": [
            {"name": "Dengue", "status": "--", "class": "risk-moderate"},
            {"name": "Gripe", "status": "--", "class": "risk-moderate"},
            {"name": "Alergia respiratória", "status": "--", "class": "risk-moderate"},
        ],
        "suggestion": "Não foi possível gerar uma sugestão climática agora.",
    }


def format_forecast(daily):
    forecast = []

    for index, date in enumerate(daily["time"]):
        weather_code = get_list_value(daily, "weather_code", index)
        max_temp = get_list_value(daily, "temperature_2m_max", index)
        min_temp = get_list_value(daily, "temperature_2m_min", index)
        rain_chance = get_list_value(daily, "precipitation_probability_max", index, 0)
        uv_index = get_list_value(daily, "uv_index_max", index)

        if rain_chance is None:
            rain_chance = 0

        forecast.append(
            {
                "date": date,
                "day_label": get_day_label(date, index),
                "icon": get_weather_icon(weather_code),
                "description": get_weather_description(weather_code),
                "max_temp": round(max_temp) if max_temp is not None else "--",
                "min_temp": round(min_temp) if min_temp is not None else "--",
                "rain_chance": rain_chance,
                "uv_index": round(uv_index) if uv_index is not None else "--",
                "risk_score": calculate_day_risk_score(
                    max_temp=max_temp,
                    min_temp=min_temp,
                    rain_chance=rain_chance,
                    uv_index=uv_index,
                    weather_code=weather_code,
                ),
            }
        )

    return forecast


def get_air_quality(latitude, longitude, timezone):
    air_url = "https://air-quality-api.open-meteo.com/v1/air-quality"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "european_aqi,pm10,pm2_5",
        "timezone": timezone,
        "forecast_days": 1,
    }

    try:
        response = requests.get(air_url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        hourly = data.get("hourly", {})

        aqi = first_available(hourly.get("european_aqi", []))
        pm10 = first_available(hourly.get("pm10", []))
        pm25 = first_available(hourly.get("pm2_5", []))

        return {
            "aqi": round(aqi) if aqi is not None else "--",
            "pm10": round(pm10, 1) if pm10 is not None else "--",
            "pm25": round(pm25, 1) if pm25 is not None else "--",
            "status": get_air_quality_status(aqi),
            "status_class": get_air_quality_class(aqi),
            "score": get_air_quality_score(aqi),
        }

    except Exception:
        return {
            "aqi": "--",
            "pm10": "--",
            "pm25": "--",
            "status": "Indisponível",
            "status_class": "",
            "score": "--",
        }


def first_available(values):
    for value in values:
        if value is not None:
            return value

    return None


def get_list_value(data, key, index, default=None):
    values = data.get(key, [])

    if index < len(values):
        return values[index]

    return default


def get_day_label(date_string, index):
    if index == 0:
        return "Hoje"

    date = datetime.strptime(date_string, "%Y-%m-%d")

    week_days = {
        0: "Seg",
        1: "Ter",
        2: "Qua",
        3: "Qui",
        4: "Sex",
        5: "Sáb",
        6: "Dom",
    }

    return week_days[date.weekday()]


def get_weather_icon(code):
    if code in [0, 1]:
        return "☀️"
    if code == 2:
        return "⛅"
    if code == 3:
        return "☁️"
    if code in [45, 48]:
        return "🌫️"
    if code in [51, 53, 55, 56, 57]:
        return "🌦️"
    if code in [61, 63, 65, 66, 67, 80, 81, 82]:
        return "🌧️"
    if code in [71, 73, 75, 77, 85, 86]:
        return "❄️"
    if code in [95, 96, 99]:
        return "⛈️"

    return "🌤️"


def get_weather_description(code):
    descriptions = {
        0: "Céu limpo",
        1: "Predominantemente limpo",
        2: "Parcialmente nublado",
        3: "Nublado",
        45: "Neblina",
        48: "Neblina intensa",
        51: "Garoa fraca",
        53: "Garoa moderada",
        55: "Garoa forte",
        56: "Garoa congelante fraca",
        57: "Garoa congelante forte",
        61: "Chuva fraca",
        63: "Chuva moderada",
        65: "Chuva forte",
        66: "Chuva congelante fraca",
        67: "Chuva congelante forte",
        71: "Neve fraca",
        73: "Neve moderada",
        75: "Neve forte",
        77: "Grãos de neve",
        80: "Pancadas de chuva",
        81: "Pancadas moderadas",
        82: "Pancadas fortes",
        85: "Pancadas de neve",
        86: "Pancadas fortes de neve",
        95: "Tempestade",
        96: "Tempestade com granizo",
        99: "Tempestade intensa",
    }

    return descriptions.get(code, "Condição climática variável")


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

    if humidity >= 90:
        score -= 15
    elif humidity >= 80:
        score -= 10
    elif humidity >= 70:
        score -= 5
    elif humidity <= 25:
        score -= 8

    if wind_speed >= 45:
        score -= 25
    elif wind_speed >= 35:
        score -= 18
    elif wind_speed >= 25:
        score -= 10
    elif wind_speed >= 18:
        score -= 5

    if rain_chance >= 80:
        score -= 30
    elif rain_chance >= 60:
        score -= 22
    elif rain_chance >= 40:
        score -= 15
    elif rain_chance >= 20:
        score -= 7

    if uv_index is not None:
        if uv_index >= 11:
            score -= 15
        elif uv_index >= 8:
            score -= 10
        elif uv_index >= 6:
            score -= 5

    if temp_max is not None and temp_min is not None:
        thermal_range = temp_max - temp_min

        if thermal_range >= 15:
            score -= 10
        elif thermal_range >= 10:
            score -= 5

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


def calculate_confidence(rain_chance, wind_speed, humidity, weather_code):
    confidence = 95

    if rain_chance >= 70:
        confidence -= 8
    elif rain_chance >= 40:
        confidence -= 4

    if wind_speed >= 35:
        confidence -= 6
    elif wind_speed >= 25:
        confidence -= 3

    if humidity >= 90:
        confidence -= 4

    if weather_code in [95, 96, 99]:
        confidence -= 10

    return max(min(round(confidence), 100), 0)


def get_score_status(score):
    if score == "--":
        return "Indisponível"

    if score >= 85:
        return "Excelente"
    if score >= 70:
        return "Favorável"
    if score >= 50:
        return "Atenção"

    return "Desfavorável"


def get_uv_label(uv_index):
    if uv_index is None:
        return "Indisponível"
    if uv_index < 3:
        return "Baixo"
    if uv_index < 6:
        return "Moderado"
    if uv_index < 8:
        return "Alto"
    if uv_index < 11:
        return "Muito alto"

    return "Extremo"


def get_uv_display(uv_index):
    if uv_index is None:
        return "Indisponível"

    return f"{round(uv_index)} ({get_uv_label(uv_index)})"


def get_pressure_status(pressure):
    if pressure is None:
        return "Indisponível"
    if pressure < 1000:
        return "Baixa"
    if pressure > 1025:
        return "Alta"

    return "Normal"


def get_pressure_score(pressure):
    if pressure is None:
        return "--"

    min_pressure = 980
    max_pressure = 1040

    score = ((pressure - min_pressure) / (max_pressure - min_pressure)) * 100

    return max(0, min(round(score), 100))


def get_air_quality_status(aqi):
    if aqi is None:
        return "Indisponível"
    if aqi <= 20:
        return "Boa"
    if aqi <= 40:
        return "Razoável"
    if aqi <= 60:
        return "Moderada"
    if aqi <= 80:
        return "Ruim"
    if aqi <= 100:
        return "Muito ruim"

    return "Perigosa"


def get_air_quality_class(aqi):
    if aqi is None:
        return ""
    if aqi <= 40:
        return "status-good"
    if aqi <= 60:
        return "status-moderate"

    return "status-bad"


def get_air_quality_score(aqi):
    if aqi is None:
        return "--"

    if aqi <= 20:
        return 90
    if aqi <= 40:
        return 75
    if aqi <= 60:
        return 55
    if aqi <= 80:
        return 35
    if aqi <= 100:
        return 15

    return 5


def calculate_day_risk_score(max_temp, min_temp, rain_chance, uv_index, weather_code):
    score = 100

    if rain_chance >= 70:
        score -= 35
    elif rain_chance >= 40:
        score -= 20
    elif rain_chance >= 20:
        score -= 8

    if max_temp is not None:
        if max_temp >= 35:
            score -= 20
        elif max_temp >= 31:
            score -= 10

    if min_temp is not None and min_temp <= 12:
        score -= 10

    if uv_index is not None and uv_index >= 8:
        score -= 8

    if weather_code in [95, 96, 99]:
        score -= 30
    elif weather_code in [61, 63, 65, 80, 81, 82]:
        score -= 15

    return max(min(round(score), 100), 0)


def get_best_window(forecast):
    if not forecast:
        return {
            "title": "Melhor janela de 5 dias",
            "text": "Não foi possível calcular a melhor janela climática.",
        }

    next_days = forecast[:5]
    best_day = max(next_days, key=lambda day: day["risk_score"])

    return {
        "title": "Melhor janela de 5 dias",
        "text": f"{best_day['day_label']} — {best_day['max_temp']}°C, {best_day['rain_chance']}% de chuva, melhor condição prevista.",
    }


def get_low_risk_day(forecast):
    if not forecast:
        return {
            "title": "Menor risco climático",
            "text": "Não foi possível calcular o menor risco climático.",
        }

    best_day = max(forecast, key=lambda day: day["risk_score"])

    return {
        "title": "Menor risco climático",
        "text": f"{best_day['day_label']} — {best_day['description']}, {best_day['rain_chance']}% de chuva.",
    }


def get_main_alert(rain_chance, wind_speed, temperature, uv_index, weather_code):
    if weather_code in [95, 96, 99]:
        return {
            "icon": "⛈️",
            "title": "Alerta de tempestade",
            "text": "Há indicação de tempestade. Evite planejar atividades ao ar livre.",
            "card_class": "danger-alert",
        }

    if rain_chance >= 70:
        return {
            "icon": "⚠️",
            "title": "Alerta de chuva forte",
            "text": f"Hoje há {rain_chance}% de probabilidade de chuva. Seu evento pode ser afetado.",
            "card_class": "danger-alert",
        }

    if wind_speed >= 35:
        return {
            "icon": "💨",
            "title": "Alerta de vento forte",
            "text": f"Ventos de até {round(wind_speed)} km/h podem afetar atividades externas.",
            "card_class": "danger-alert",
        }

    if temperature >= 34:
        return {
            "icon": "🌡️",
            "title": "Alerta de calor",
            "text": f"Temperatura elevada de {round(temperature)}°C. Evite exposição prolongada ao sol.",
            "card_class": "danger-alert",
        }

    if uv_index is not None and uv_index >= 8:
        return {
            "icon": "🧴",
            "title": "Índice UV muito alto",
            "text": f"Índice UV previsto em {round(uv_index)}. Use proteção solar.",
            "card_class": "danger-alert",
        }

    return {
        "icon": "✅",
        "title": "Sem alerta climático importante",
        "text": "As condições gerais estão favoráveis no momento.",
        "card_class": "safe-alert",
    }


def generate_recommendations(temperature, humidity, rain_chance, uv_index, wind_speed):
    recommendations = []

    if rain_chance >= 50:
        recommendations.append(
            {
                "icon": "☂️",
                "title": "Leve guarda-chuva",
                "text": "A chance de chuva está alta. Planeje deslocamentos com cuidado.",
            }
        )

    if temperature >= 30:
        recommendations.append(
            {
                "icon": "💧",
                "title": "Hidratação",
                "text": "Temperatura elevada. Mantenha uma garrafa de água por perto.",
            }
        )

    if uv_index is not None and uv_index >= 6:
        recommendations.append(
            {
                "icon": "🧴",
                "title": "Proteção solar",
                "text": f"Índice UV {get_uv_label(uv_index).lower()}. Use protetor solar se sair durante o dia.",
            }
        )

    if wind_speed >= 25:
        recommendations.append(
            {
                "icon": "💨",
                "title": "Atenção ao vento",
                "text": "Evite objetos soltos e tenha cuidado em atividades ao ar livre.",
            }
        )

    if humidity >= 80:
        recommendations.append(
            {
                "icon": "🌫️",
                "title": "Umidade elevada",
                "text": "O clima pode parecer mais abafado. Prefira locais ventilados.",
            }
        )

    if not recommendations:
        recommendations.append(
            {
                "icon": "🚶",
                "title": "Atividades ao ar livre",
                "text": "Boas condições para atividades externas no momento.",
            }
        )

    return recommendations[:3]


def calculate_disease_risks(temperature, humidity, rain_chance, air_quality):
    risks = []

    if temperature >= 24 and humidity >= 70 and rain_chance >= 50:
        dengue_status = "Alto"
        dengue_class = "risk-high"
    elif temperature >= 22 and humidity >= 60:
        dengue_status = "Moderado"
        dengue_class = "risk-moderate"
    else:
        dengue_status = "Baixo"
        dengue_class = "risk-low"

    risks.append(
        {
            "name": "Dengue",
            "status": dengue_status,
            "class": dengue_class,
        }
    )

    if temperature <= 18 and humidity >= 70:
        flu_status = "Moderado"
        flu_class = "risk-moderate"
    else:
        flu_status = "Baixo"
        flu_class = "risk-low"

    risks.append(
        {
            "name": "Gripe",
            "status": flu_status,
            "class": flu_class,
        }
    )

    aqi = air_quality.get("aqi")

    if isinstance(aqi, int) and aqi >= 60:
        allergy_status = "Alto"
        allergy_class = "risk-high"
    elif humidity <= 35 or (isinstance(aqi, int) and aqi >= 40):
        allergy_status = "Moderado"
        allergy_class = "risk-moderate"
    else:
        allergy_status = "Baixo"
        allergy_class = "risk-low"

    risks.append(
        {
            "name": "Alergia respiratória",
            "status": allergy_status,
            "class": allergy_class,
        }
    )

    return risks


def generate_suggestion(today_rain_chance, uv_index, best_window):
    if today_rain_chance >= 60:
        return f"Considere remarcar atividades ao ar livre. {best_window['text']}"

    if uv_index is not None and uv_index >= 8:
        return "Prefira atividades ao ar livre no início da manhã ou no fim da tarde, quando a exposição ao sol costuma ser menor."

    return "As condições estão favoráveis. Mantenha o planejamento e acompanhe possíveis mudanças na previsão."