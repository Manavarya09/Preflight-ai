"""
Weather API clients for PreFlight AI
Integrates OpenWeatherMap and NOAA Aviation Weather
"""
import os
from datetime import datetime
from typing import Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class WeatherAPIError(Exception):
    """Custom exception for weather API errors"""

    pass


class OpenWeatherMapClient:
    """
    Client for OpenWeatherMap API
    Provides real-time weather data for airports
    """

    BASE_URL = "https://api.openweathermap.org/data/2.5"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENWEATHER_API_KEY")
        if not self.api_key:
            raise ValueError("OpenWeatherMap API key not provided")

        # Configure session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_airport_weather(self, airport_code: str) -> Dict:
        """
        Get current weather for an airport.

        Args:
            airport_code: IATA airport code (e.g., 'DXB', 'LHR')

        Returns:
            dict: Standardized weather data

        Raises:
            WeatherAPIError: If API call fails
        """
        try:
            # In production, you'd map airport codes to coordinates or city names
            # For now, using a simple mapping
            airport_mapping = {
                "DXB": "Dubai",
                "LHR": "London",
                "JFK": "New York",
                "LAX": "Los Angeles",
                "SIN": "Singapore",
                "FRA": "Frankfurt",
                "NRT": "Tokyo",
                "DEL": "New Delhi",
                "CDG": "Paris",
            }

            city = airport_mapping.get(airport_code, airport_code)

            response = self.session.get(
                f"{self.BASE_URL}/weather",
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()

            return self._parse_weather_response(data, airport_code)

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"OpenWeatherMap API error: {str(e)}")

    def _parse_weather_response(self, data: Dict, airport_code: str) -> Dict:
        """
        Parse OpenWeatherMap response into standardized format.
        """
        # Convert wind speed from m/s to knots (1 m/s = 1.94384 knots)
        wind_speed_ms = data.get("wind", {}).get("speed", 0)
        wind_speed_kts = wind_speed_ms * 1.94384

        wind_gust_ms = data.get("wind", {}).get("gust", 0)
        wind_gust_kts = wind_gust_ms * 1.94384 if wind_gust_ms else None

        # Visibility is in meters, convert to km
        visibility_m = data.get("visibility", 10000)
        visibility_km = visibility_m / 1000

        # Determine precipitation
        rain = data.get("rain", {}).get("1h", 0)
        snow = data.get("snow", {}).get("1h", 0)
        precipitation_mm = rain + snow

        precipitation_type = "NONE"
        if rain > 0:
            precipitation_type = "RAIN"
        elif snow > 0:
            precipitation_type = "SNOW"

        # Check for thunderstorms
        weather_conditions = data.get("weather", [])
        thunderstorm_nearby = any(
            w.get("main", "").upper() == "THUNDERSTORM" for w in weather_conditions
        )

        return {
            "airport_code": airport_code,
            "timestamp": datetime.fromtimestamp(data.get("dt", datetime.now().timestamp())),
            "temperature_c": data.get("main", {}).get("temp", 15.0),
            "wind_speed_kts": round(wind_speed_kts, 2),
            "wind_direction_deg": data.get("wind", {}).get("deg", 0),
            "wind_gust_kts": round(wind_gust_kts, 2) if wind_gust_kts else None,
            "visibility_km": round(visibility_km, 2),
            "cloud_coverage_percent": data.get("clouds", {}).get("all", 0),
            "precipitation_type": precipitation_type,
            "precipitation_mm": round(precipitation_mm, 2),
            "pressure_mb": data.get("main", {}).get("pressure", 1013),
            "humidity_percent": data.get("main", {}).get("humidity", 50),
            "wind_shear_alert": False,  # OpenWeatherMap doesn't provide this
            "thunderstorm_nearby": thunderstorm_nearby,
            "data_source": "OPENWEATHERMAP",
            "conditions_description": weather_conditions[0].get("description", "")
            if weather_conditions
            else "",
        }

    def get_forecast(self, airport_code: str, hours: int = 48) -> list:
        """
        Get weather forecast for an airport.

        Args:
            airport_code: IATA airport code
            hours: Number of hours to forecast (default 48)

        Returns:
            list: List of weather forecasts
        """
        try:
            airport_mapping = {
                "DXB": "Dubai",
                "LHR": "London",
                "JFK": "New York",
                "LAX": "Los Angeles",
            }
            city = airport_mapping.get(airport_code, airport_code)

            response = self.session.get(
                f"{self.BASE_URL}/forecast",
                params={"q": city, "appid": self.api_key, "units": "metric"},
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()

            forecasts = []
            for item in data.get("list", [])[:hours // 3]:  # Data is in 3-hour intervals
                forecasts.append(self._parse_weather_response(item, airport_code))

            return forecasts

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"Forecast API error: {str(e)}")


class NOAAWeatherClient:
    """
    Client for NOAA Aviation Weather Center
    Provides METAR reports and aviation-specific weather data
    """

    BASE_URL = "https://aviationweather.gov/api/data"

    def __init__(self):
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504])
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_metar(self, airport_code: str) -> Dict:
        """
        Get METAR report for an airport.

        Args:
            airport_code: ICAO airport code (4-letter, e.g., 'OMDB' for Dubai)

        Returns:
            dict: Parsed METAR data
        """
        try:
            # Convert IATA to ICAO if needed
            icao_code = self._iata_to_icao(airport_code)

            response = self.session.get(
                f"{self.BASE_URL}/metar",
                params={"ids": icao_code, "format": "json"},
                timeout=10,
            )

            response.raise_for_status()
            data = response.json()

            if not data:
                raise WeatherAPIError(f"No METAR data found for {airport_code}")

            return self._parse_metar(data[0], airport_code)

        except requests.exceptions.RequestException as e:
            raise WeatherAPIError(f"NOAA API error: {str(e)}")

    def _iata_to_icao(self, iata_code: str) -> str:
        """
        Convert IATA code to ICAO code.
        In production, use a comprehensive database.
        """
        mapping = {
            "DXB": "OMDB",
            "LHR": "EGLL",
            "JFK": "KJFK",
            "LAX": "KLAX",
            "SIN": "WSSS",
            "FRA": "EDDF",
            "NRT": "RJAA",
            "DEL": "VIDP",
        }
        return mapping.get(iata_code, iata_code)

    def _parse_metar(self, metar_data: Dict, airport_code: str) -> Dict:
        """
        Parse NOAA METAR response.
        """
        # This is a simplified parser. Production would use a proper METAR decoder.
        return {
            "airport_code": airport_code,
            "metar_raw": metar_data.get("rawOb", ""),
            "timestamp": datetime.fromisoformat(metar_data.get("obsTime", datetime.now().isoformat())),
            "temperature_c": metar_data.get("temp", 15.0),
            "wind_speed_kts": metar_data.get("wspd", 0),
            "wind_direction_deg": metar_data.get("wdir", 0),
            "visibility_km": metar_data.get("visib", 10.0),
            "data_source": "NOAA",
        }


# ============================================================================
# Unified Weather Service
# ============================================================================


class WeatherService:
    """
    Unified weather service that tries multiple providers.
    Falls back gracefully if primary provider fails.
    """

    def __init__(self):
        try:
            self.openweather = OpenWeatherMapClient()
        except ValueError:
            self.openweather = None
            print("Warning: OpenWeatherMap not configured")

        self.noaa = NOAAWeatherClient()

    def get_weather(self, airport_code: str) -> Dict:
        """
        Get weather from available provider.
        Tries OpenWeatherMap first, falls back to NOAA.

        Args:
            airport_code: IATA airport code

        Returns:
            dict: Weather data
        """
        # Try OpenWeatherMap first (more detailed)
        if self.openweather:
            try:
                return self.openweather.get_airport_weather(airport_code)
            except WeatherAPIError as e:
                print(f"OpenWeatherMap failed: {e}, trying NOAA...")

        # Fall back to NOAA
        try:
            return self.noaa.get_metar(airport_code)
        except WeatherAPIError as e:
            print(f"NOAA failed: {e}")
            # Return default/cached data
            return self._get_default_weather(airport_code)

    def _get_default_weather(self, airport_code: str) -> Dict:
        """
        Return default weather when all APIs fail.
        In production, this would return cached data from database.
        """
        return {
            "airport_code": airport_code,
            "timestamp": datetime.now(),
            "temperature_c": 15.0,
            "wind_speed_kts": 5.0,
            "wind_direction_deg": 270,
            "visibility_km": 10.0,
            "cloud_coverage_percent": 50,
            "precipitation_type": "NONE",
            "precipitation_mm": 0.0,
            "pressure_mb": 1013.0,
            "humidity_percent": 50,
            "data_source": "DEFAULT",
            "error": "All weather APIs unavailable",
        }


# ============================================================================
# For backwards compatibility
# ============================================================================

def get_weather_service() -> WeatherService:
    """Get singleton weather service instance."""
    return WeatherService()


__all__ = [
    "WeatherAPIError",
    "OpenWeatherMapClient",
    "NOAAWeatherClient",
    "WeatherService",
    "get_weather_service",
]
