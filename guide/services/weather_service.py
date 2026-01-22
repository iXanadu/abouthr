"""
Weather Service using Open-Meteo API

Provides current weather and forecast for Hampton Roads cities.
No API key required - completely free.

API Documentation: https://open-meteo.com/en/docs
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import requests
from django.core.cache import cache

logger = logging.getLogger(__name__)

# Hampton Roads city coordinates
CITY_COORDINATES = {
    'virginia-beach': {'lat': 36.8529, 'lon': -75.9780, 'name': 'Virginia Beach'},
    'norfolk': {'lat': 36.8508, 'lon': -76.2859, 'name': 'Norfolk'},
    'chesapeake': {'lat': 36.7682, 'lon': -76.2875, 'name': 'Chesapeake'},
    'newport-news': {'lat': 37.0871, 'lon': -76.4730, 'name': 'Newport News'},
    'hampton': {'lat': 37.0299, 'lon': -76.3452, 'name': 'Hampton'},
    'portsmouth': {'lat': 36.8354, 'lon': -76.2983, 'name': 'Portsmouth'},
    'suffolk': {'lat': 36.7282, 'lon': -76.5836, 'name': 'Suffolk'},
    'williamsburg': {'lat': 37.2707, 'lon': -76.7075, 'name': 'Williamsburg'},
    'poquoson': {'lat': 37.1224, 'lon': -76.3458, 'name': 'Poquoson'},
}

# Weather code descriptions from Open-Meteo
WEATHER_CODES = {
    0: ('Clear sky', 'sun', 'clear'),
    1: ('Mainly clear', 'sun', 'clear'),
    2: ('Partly cloudy', 'cloud-sun', 'partly-cloudy'),
    3: ('Overcast', 'clouds', 'cloudy'),
    45: ('Foggy', 'cloud-fog', 'fog'),
    48: ('Depositing rime fog', 'cloud-fog', 'fog'),
    51: ('Light drizzle', 'cloud-drizzle', 'drizzle'),
    53: ('Moderate drizzle', 'cloud-drizzle', 'drizzle'),
    55: ('Dense drizzle', 'cloud-drizzle', 'drizzle'),
    56: ('Light freezing drizzle', 'cloud-sleet', 'freezing'),
    57: ('Dense freezing drizzle', 'cloud-sleet', 'freezing'),
    61: ('Slight rain', 'cloud-rain', 'rain'),
    63: ('Moderate rain', 'cloud-rain', 'rain'),
    65: ('Heavy rain', 'cloud-rain-heavy', 'rain'),
    66: ('Light freezing rain', 'cloud-sleet', 'freezing'),
    67: ('Heavy freezing rain', 'cloud-sleet', 'freezing'),
    71: ('Slight snow', 'cloud-snow', 'snow'),
    73: ('Moderate snow', 'cloud-snow', 'snow'),
    75: ('Heavy snow', 'cloud-snow', 'snow'),
    77: ('Snow grains', 'cloud-snow', 'snow'),
    80: ('Slight rain showers', 'cloud-rain', 'showers'),
    81: ('Moderate rain showers', 'cloud-rain', 'showers'),
    82: ('Violent rain showers', 'cloud-rain-heavy', 'showers'),
    85: ('Slight snow showers', 'cloud-snow', 'snow'),
    86: ('Heavy snow showers', 'cloud-snow', 'snow'),
    95: ('Thunderstorm', 'cloud-lightning', 'thunderstorm'),
    96: ('Thunderstorm with slight hail', 'cloud-lightning-rain', 'thunderstorm'),
    99: ('Thunderstorm with heavy hail', 'cloud-lightning-rain', 'thunderstorm'),
}


@dataclass
class CurrentWeather:
    """Current weather conditions."""
    temperature: float  # Fahrenheit
    feels_like: float  # Fahrenheit
    humidity: int  # Percentage
    wind_speed: float  # mph
    wind_direction: int  # degrees
    weather_code: int
    description: str
    icon: str  # Bootstrap icon name
    condition: str  # Simple condition category
    is_day: bool
    timestamp: datetime


@dataclass
class DailyForecast:
    """Daily forecast data."""
    date: datetime
    high: float  # Fahrenheit
    low: float  # Fahrenheit
    weather_code: int
    description: str
    icon: str
    condition: str
    precipitation_chance: int  # Percentage
    precipitation_sum: float  # inches


@dataclass
class WeatherData:
    """Complete weather data for a location."""
    city_name: str
    city_slug: str
    current: CurrentWeather
    forecast: list[DailyForecast]
    fetched_at: datetime


class WeatherService:
    """
    Service for fetching weather data from Open-Meteo API.

    Features:
    - Current conditions with feels-like temperature
    - 5-day forecast
    - Automatic caching (15 minutes for current, 1 hour for forecast)
    - No API key required
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"
    CACHE_TIMEOUT_CURRENT = 900  # 15 minutes
    CACHE_TIMEOUT_FORECAST = 3600  # 1 hour

    def get_weather(self, city_slug: str) -> Optional[WeatherData]:
        """
        Get current weather and forecast for a city.

        Args:
            city_slug: The city's URL slug (e.g., 'virginia-beach')

        Returns:
            WeatherData object or None if city not found or API error
        """
        coords = CITY_COORDINATES.get(city_slug)
        if not coords:
            logger.warning(f"Unknown city slug for weather: {city_slug}")
            return None

        # Check cache first
        cache_key = f"weather_{city_slug}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        try:
            weather_data = self._fetch_weather(city_slug, coords)
            if weather_data:
                cache.set(cache_key, weather_data, self.CACHE_TIMEOUT_CURRENT)
            return weather_data
        except Exception as e:
            logger.error(f"Error fetching weather for {city_slug}: {e}")
            return None

    def get_current_weather(self, city_slug: str) -> Optional[CurrentWeather]:
        """Get just the current weather conditions."""
        data = self.get_weather(city_slug)
        return data.current if data else None

    def get_forecast(self, city_slug: str, days: int = 5) -> Optional[list[DailyForecast]]:
        """Get forecast for specified number of days."""
        data = self.get_weather(city_slug)
        if data:
            return data.forecast[:days]
        return None

    def get_regional_weather(self) -> dict[str, WeatherData]:
        """
        Get weather for all Hampton Roads cities.

        Returns:
            Dict mapping city slugs to WeatherData
        """
        results = {}
        for city_slug in CITY_COORDINATES.keys():
            weather = self.get_weather(city_slug)
            if weather:
                results[city_slug] = weather
        return results

    def _fetch_weather(self, city_slug: str, coords: dict) -> Optional[WeatherData]:
        """Fetch weather data from Open-Meteo API."""
        params = {
            'latitude': coords['lat'],
            'longitude': coords['lon'],
            'current': [
                'temperature_2m',
                'relative_humidity_2m',
                'apparent_temperature',
                'weather_code',
                'wind_speed_10m',
                'wind_direction_10m',
                'is_day',
            ],
            'daily': [
                'weather_code',
                'temperature_2m_max',
                'temperature_2m_min',
                'precipitation_sum',
                'precipitation_probability_max',
            ],
            'temperature_unit': 'fahrenheit',
            'wind_speed_unit': 'mph',
            'precipitation_unit': 'inch',
            'timezone': 'America/New_York',
            'forecast_days': 5,
        }

        response = requests.get(self.BASE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        # Parse current weather
        current_data = data.get('current', {})
        weather_code = current_data.get('weather_code', 0)
        desc, icon, condition = WEATHER_CODES.get(weather_code, ('Unknown', 'question', 'unknown'))

        current = CurrentWeather(
            temperature=round(current_data.get('temperature_2m', 0)),
            feels_like=round(current_data.get('apparent_temperature', 0)),
            humidity=current_data.get('relative_humidity_2m', 0),
            wind_speed=round(current_data.get('wind_speed_10m', 0)),
            wind_direction=current_data.get('wind_direction_10m', 0),
            weather_code=weather_code,
            description=desc,
            icon=f"bi-{icon}",
            condition=condition,
            is_day=bool(current_data.get('is_day', 1)),
            timestamp=datetime.fromisoformat(current_data.get('time', datetime.now().isoformat())),
        )

        # Parse daily forecast
        daily_data = data.get('daily', {})
        forecast = []

        dates = daily_data.get('time', [])
        highs = daily_data.get('temperature_2m_max', [])
        lows = daily_data.get('temperature_2m_min', [])
        codes = daily_data.get('weather_code', [])
        precip_sums = daily_data.get('precipitation_sum', [])
        precip_chances = daily_data.get('precipitation_probability_max', [])

        for i in range(len(dates)):
            code = codes[i] if i < len(codes) else 0
            desc, icon, condition = WEATHER_CODES.get(code, ('Unknown', 'question', 'unknown'))

            forecast.append(DailyForecast(
                date=datetime.fromisoformat(dates[i]),
                high=round(highs[i]) if i < len(highs) else 0,
                low=round(lows[i]) if i < len(lows) else 0,
                weather_code=code,
                description=desc,
                icon=f"bi-{icon}",
                condition=condition,
                precipitation_chance=precip_chances[i] if i < len(precip_chances) else 0,
                precipitation_sum=round(precip_sums[i], 2) if i < len(precip_sums) else 0,
            ))

        return WeatherData(
            city_name=coords['name'],
            city_slug=city_slug,
            current=current,
            forecast=forecast,
            fetched_at=datetime.now(),
        )


# Singleton instance for convenience
weather_service = WeatherService()
