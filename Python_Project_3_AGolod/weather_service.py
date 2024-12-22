import requests
from typing import Dict, Any, List

from config import ACCUWEATHER_API_KEY


def get_city_data(city_name: str) -> Dict[str, Any]:
    """
    Выполняет поиск города (city_name) через AccuWeather
    и возвращает информацию о месте:
      - "city_key": ключ для последующих запросов
      - "latitude": широта
      - "longitude": долгота
      - "city_name": исходное название города

    :param city_name: Название города (строка)
    :return: Словарь {"city_key", "latitude", "longitude", "city_name"}
    :raises ValueError: Если город не найден
    """
    search_url = "http://dataservice.accuweather.com/locations/v1/cities/search"
    params = {
        "apikey": ACCUWEATHER_API_KEY,
        "q": city_name,
        "language": "en-us"
    }

    resp = requests.get(search_url, params=params, timeout=10)
    resp.raise_for_status()
    results: List[Dict[str, Any]] = resp.json()

    if not results:
        raise ValueError(f"Город не обнаружен: {city_name}")

    best_match = results[0]
    location_key = best_match.get("Key", "")
    geo_info = best_match.get("GeoPosition", {})
    lat = geo_info.get("Latitude", 0.0)
    lon = geo_info.get("Longitude", 0.0)

    return {
        "city_key": location_key,
        "latitude": lat,
        "longitude": lon,
        "city_name": city_name
    }


def get_extended_forecast(city_key: str, days: int) -> Dict[str, Any]:
    """
    Запрашивает ежедневный прогноз погоды на указанное количество дней
    (1, 3 или 5) через AccuWeather.

    :param city_key: Идентификатор города
    :param days: Число дней (1, 3 или 5)
    :return: Сырой словарь прогноза
    :raises ValueError: Если days не входит в [1, 3, 5]
    """
    if days not in [1, 3, 5]:
        raise ValueError("Допустимое количество дней прогноза: 1, 3 или 5.")

    base_url = f"http://dataservice.accuweather.com/forecasts/v1/daily/5day/{city_key}"
    params = {
        "apikey": ACCUWEATHER_API_KEY,
        "language": "en-us",
        "metric": "true"
    }

    response = requests.get(base_url, params=params, timeout=10)
    response.raise_for_status()
    data: Dict[str, Any] = response.json()

    # Оставляем только нужное кол-во дней
    if "DailyForecasts" in data:
        data["DailyForecasts"] = data["DailyForecasts"][:days]

    return data
