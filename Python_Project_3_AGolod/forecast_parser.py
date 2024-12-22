from typing import Dict, Any, List

def process_forecast_data(raw_forecast: Dict[str, Any]) -> Dict[str, List]:
    """
    Преобразует полученный JSON от AccuWeather в структуру:
      {
        "dates": [...],
        "min_temps": [...],
        "max_temps": [...],
        "winds": [...],
        "precip_chances": [...]
      }

    :param raw_forecast: Сырой JSON прогноза
    :return: Словарь со списками необходимых значений
    """
    daily_entries = raw_forecast.get("DailyForecasts", [])
    result = {
        "dates": [],
        "min_temps": [],
        "max_temps": [],
        "winds": [],
        "precip_chances": []
    }

    for day_data in daily_entries:
        # Извлекаем дату (формат 'YYYY-MM-DD' до символа 'T')
        date_str = day_data.get("Date", "").split("T")[0]

        # Температура
        temp_info = day_data.get("Temperature", {})
        min_temp = temp_info.get("Minimum", {}).get("Value", 0.0)
        max_temp = temp_info.get("Maximum", {}).get("Value", 0.0)

        # Дневные параметры
        day_part = day_data.get("Day", {})
        wind_info = day_part.get("Wind", {})
        wind_speed = wind_info.get("Speed", {}).get("Value", 0.0)

        precipitation_probability = day_part.get("PrecipitationProbability", 0)

        result["dates"].append(date_str)
        result["min_temps"].append(min_temp)
        result["max_temps"].append(max_temp)
        result["winds"].append(wind_speed)
        result["precip_chances"].append(precipitation_probability)

    return result
