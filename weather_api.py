"""
weather_api.py
--------------
Lightweight helper module that provides:
  * POPULAR_CITIES  - a list of city names for the dropdown menu
  * get_user_location() - detects the user's approximate location via their
                           public IP address (no API key required)
  * fetch_weather(city) - looks up a city by name and returns current
                           weather + a short hourly forecast
  * fetch_weather_by_coords(lat, lon, label, country) - same as above but
                           using known coordinates (used for auto-detect,
                           since it avoids an extra/ambiguous name search)

Data sources (both completely free, no API key required):
  * IP geolocation : http://ip-api.com/json/
  * Geocoding      : https://geocoding-api.open-meteo.com/v1/search
  * Forecast       : https://api.open-meteo.com/v1/forecast
"""

import requests

POPULAR_CITIES = [
    "Mumbai", "Delhi", "Bengaluru", "New York", "London", "Paris",
    "Tokyo", "Sydney", "Dubai", "Singapore", "Toronto", "Berlin",
    "Moscow", "Cape Town", "Sao Paulo",
]

_GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
_IP_LOOKUP_URL = "http://ip-api.com/json/"

_REQUEST_TIMEOUT = 6

_WEATHER_CODES = {
    0: ("Clear sky", "☀️"),
    1: ("Mostly clear", "🌤️"),
    2: ("Partly cloudy", "⛅"),
    3: ("Overcast", "☁️"),
    45: ("Foggy", "🌫️"),
    48: ("Depositing rime fog", "🌫️"),
    51: ("Light drizzle", "🌦️"),
    53: ("Moderate drizzle", "🌦️"),
    55: ("Dense drizzle", "🌧️"),
    56: ("Freezing drizzle", "🌧️"),
    57: ("Freezing drizzle", "🌧️"),
    61: ("Slight rain", "🌦️"),
    63: ("Moderate rain", "🌧️"),
    65: ("Heavy rain", "🌧️"),
    66: ("Freezing rain", "🌧️"),
    67: ("Freezing rain", "🌧️"),
    71: ("Slight snow fall", "🌨️"),
    73: ("Moderate snow fall", "🌨️"),
    75: ("Heavy snow fall", "❄️"),
    77: ("Snow grains", "❄️"),
    80: ("Slight rain showers", "🌦️"),
    81: ("Moderate rain showers", "🌧️"),
    82: ("Violent rain showers", "⛈️"),
    85: ("Slight snow showers", "🌨️"),
    86: ("Heavy snow showers", "❄️"),
    95: ("Thunderstorm", "⛈️"),
    96: ("Thunderstorm with hail", "⛈️"),
    99: ("Thunderstorm with hail", "⛈️"),
}


def _describe_weather_code(code):
    return _WEATHER_CODES.get(int(code), ("Unknown", "🌡️"))

def get_user_location():
    try:
        response = requests.get(_IP_LOOKUP_URL, timeout=_REQUEST_TIMEOUT)
        data = response.json()
        if data.get("status") == "success":
            return {
                "city": data.get("city", "Your Location"),
                "country": data.get("country", ""),
                "lat": data.get("lat"),
                "lon": data.get("lon"),
            }
    except (requests.RequestException, ValueError):
        pass
    return None


def _build_weather_result(lat, lon, city_name, country):
    try:
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,wind_speed_10m,weather_code",
            "hourly": "temperature_2m,weather_code",
            "daily": "uv_index_max",
            "timezone": "auto",
            "forecast_days": 1,
        }
        response = requests.get(_FORECAST_URL, params=params, timeout=_REQUEST_TIMEOUT)
        payload = response.json()

        current = payload.get("current", {})
        hourly = payload.get("hourly", {})
        daily = payload.get("daily", {})

        weather_code = current.get("weather_code", 0)
        description, icon = _describe_weather_code(weather_code)
        hourly_forecast = []
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        codes = hourly.get("weather_code", [])
        current_time = current.get("time")

        start_index = 0
        if current_time in times:
            start_index = times.index(current_time)

        for i in range(start_index, min(start_index + 6, len(times))):
            hour_label = _format_hour_label(times[i], is_now=(i == start_index))
            _, hour_icon = _describe_weather_code(codes[i]) if i < len(codes) else ("", "🌡️")
            hour_temp = round(temps[i]) if i < len(temps) else "--"
            hourly_forecast.append({"time": hour_label, "temp": f"{hour_temp}°", "icon": hour_icon})

        uv_values = daily.get("uv_index_max", [])
        uv_index = round(uv_values[0], 1) if uv_values else "--"

        return {
            "success": True,
            "city": city_name,
            "country": country,
            "temp": round(current.get("temperature_2m", 0)),
            "description": description,
            "icon": icon,
            "humidity": f"{round(current.get('relative_humidity_2m', 0))}%",
            "wind": f"{round(current.get('wind_speed_10m', 0))} km/h",
            "uv": uv_index,
            "hourly": hourly_forecast,
        }
    except (requests.RequestException, ValueError, KeyError, IndexError):
        return {"success": False, "error": "Unable to retrieve weather data."}


def _format_hour_label(iso_time, is_now=False):
    if is_now:
        return "Now"
    try:
        hour = int(iso_time.split("T")[1].split(":")[0])
    except (IndexError, ValueError):
        return "--"
    period = "AM" if hour < 12 else "PM"
    display_hour = hour % 12
    if display_hour == 0:
        display_hour = 12
    return f"{display_hour}{period}"


def fetch_weather(city: str):
    if not city:
        return {"success": False, "error": "Please provide a city name."}

    try:
        response = requests.get(
            _GEOCODE_URL, params={"name": city, "count": 1}, timeout=_REQUEST_TIMEOUT
        )
        results = response.json().get("results")
        if not results:
            return {"success": False, "error": f"Could not find '{city}'."}

        match = results[0]
        return _build_weather_result(
            match["latitude"], match["longitude"], match.get("name", city), match.get("country", "")
        )
    except (requests.RequestException, ValueError, KeyError):
        return {"success": False, "error": "Unable to reach weather service."}


def fetch_weather_by_coords(lat: float, lon: float, city: str = "Your Location", country: str = ""):
    if lat is None or lon is None:
        return {"success": False, "error": "Location coordinates unavailable."}
    return _build_weather_result(lat, lon, city, country)
