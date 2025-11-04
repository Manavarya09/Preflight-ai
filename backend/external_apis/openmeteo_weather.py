"""
Open-Meteo Weather API Client for PreFlight AI
Free, high-resolution weather forecasts for aviation
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class OpenMeteoError(Exception):
    """Custom exception for Open-Meteo API errors"""
    pass


# Airport coordinates database (IATA code -> lat, lon)
AIRPORT_COORDINATES = {
    "DXB": (25.2532, 55.3657),  # Dubai
    "LHR": (51.4700, -0.4543),  # London Heathrow
    "JFK": (40.6413, -73.7781),  # New York JFK
    "LAX": (33.9416, -118.4085),  # Los Angeles
    "SIN": (1.3644, 103.9915),  # Singapore
    "FRA": (50.0379, 8.5622),  # Frankfurt
    "NRT": (35.7653, 140.3856),  # Tokyo Narita
    "DEL": (28.5562, 77.1000),  # New Delhi
    "CDG": (49.0097, 2.5479),  # Paris Charles de Gaulle
    "AMS": (52.3105, 4.7683),  # Amsterdam
    "HKG": (22.3080, 113.9185),  # Hong Kong
    "SYD": (-33.9399, 151.1753),  # Sydney
    "ORD": (41.9742, -87.9073),  # Chicago O'Hare
    "ATL": (33.6407, -84.4277),  # Atlanta
    "DFW": (32.8998, -97.0403),  # Dallas/Fort Worth
}


class OpenMeteoClient:
    """
    Client for Open-Meteo API
    Provides high-resolution weather forecasts for airports
    """

    BASE_URL = "https://api.open-meteo.com/v1/forecast"

    def __init__(self):
        # Open-Meteo is free and doesn't require an API key!
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_airport_coordinates(self, airport_code: str) -> Tuple[float, float]:
        """
        Get latitude and longitude for an airport.

        Args:
            airport_code: IATA airport code

        Returns:
            tuple: (latitude, longitude)
        """
        coords = AIRPORT_COORDINATES.get(airport_code.upper())
        if not coords:
            raise OpenMeteoError(
                f"Airport coordinates not found for {airport_code}. "
                f"Please add to AIRPORT_COORDINATES."
            )
        return coords

    def get_current_weather(self, airport_code: str) -> Dict:
        """
        Get current weather for an airport.

        Args:
            airport_code: IATA airport code

        Returns:
            dict: Current weather data
        """
        try:
            lat, lon = self.get_airport_coordinates(airport_code)

            params = {
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m",
                    "cloud_cover",
                    "surface_pressure",
                    "visibility",
                ],
                "wind_speed_unit": "kn",  # Knots for aviation
                "temperature_unit": "celsius",
            }

            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_current_weather(data, airport_code)

        except requests.exceptions.RequestException as e:
            raise OpenMeteoError(f"Open-Meteo API error: {str(e)}")

    def get_hourly_forecast(
        self, airport_code: str, hours: int = 48
    ) -> List[Dict]:
        """
        Get hourly weather forecast for an airport.

        Args:
            airport_code: IATA airport code
            hours: Number of hours to forecast (default 48, max 168)

        Returns:
            list: Hourly weather forecasts
        """
        try:
            lat, lon = self.get_airport_coordinates(airport_code)

            params = {
                "latitude": lat,
                "longitude": lon,
                "hourly": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "precipitation_probability",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m",
                    "cloud_cover",
                    "surface_pressure",
                    "visibility",
                    "weather_code",
                ],
                "wind_speed_unit": "kn",
                "temperature_unit": "celsius",
                "forecast_days": min(7, (hours // 24) + 1),
            }

            response = self.session.get(self.BASE_URL, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            return self._parse_hourly_forecast(data, airport_code, hours)

        except requests.exceptions.RequestException as e:
            raise OpenMeteoError(f"Hourly forecast error: {str(e)}")

    def get_weather_at_time(
        self, airport_code: str, target_datetime: datetime
    ) -> Dict:
        """
        Get weather forecast for a specific datetime.

        Args:
            airport_code: IATA airport code
            target_datetime: Target datetime for weather forecast

        Returns:
            dict: Weather data at specified time
        """
        hourly_forecast = self.get_hourly_forecast(airport_code, hours=168)  # 7 days

        # Find closest forecast to target time
        closest_forecast = None
        min_diff = float("inf")

        for forecast in hourly_forecast:
            forecast_time = datetime.fromisoformat(forecast["timestamp"])
            diff = abs((forecast_time - target_datetime).total_seconds())

            if diff < min_diff:
                min_diff = diff
                closest_forecast = forecast

        if not closest_forecast:
            raise OpenMeteoError("No forecast data available for the target time")

        return closest_forecast

    def get_aviation_weather_briefing(self, airport_code: str) -> Dict:
        """
        Get comprehensive aviation weather briefing for an airport.

        Args:
            airport_code: IATA airport code

        Returns:
            dict: Comprehensive weather briefing
        """
        current = self.get_current_weather(airport_code)
        forecast_6h = self.get_hourly_forecast(airport_code, hours=6)
        forecast_24h = self.get_hourly_forecast(airport_code, hours=24)

        # Calculate weather trends
        wind_increasing = False
        visibility_deteriorating = False
        precipitation_expected = False

        if len(forecast_6h) >= 2:
            wind_increasing = forecast_6h[-1]["wind_speed_kts"] > forecast_6h[0]["wind_speed_kts"] * 1.5
            visibility_deteriorating = forecast_6h[-1]["visibility_km"] < forecast_6h[0]["visibility_km"] * 0.7
            precipitation_expected = any(f["precipitation_mm"] > 0.5 for f in forecast_6h)

        # Determine operational concerns
        concerns = []
        if current["wind_speed_kts"] > 25:
            concerns.append("HIGH_WINDS")
        if current["wind_gust_kts"] and current["wind_gust_kts"] > 35:
            concerns.append("SEVERE_GUSTS")
        if current["visibility_km"] < 5:
            concerns.append("LOW_VISIBILITY")
        if current["precipitation_mm"] > 2:
            concerns.append("HEAVY_PRECIPITATION")
        if wind_increasing:
            concerns.append("WIND_INCREASING")
        if visibility_deteriorating:
            concerns.append("VISIBILITY_DETERIORATING")
        if precipitation_expected:
            concerns.append("PRECIPITATION_EXPECTED")

        return {
            "airport_code": airport_code,
            "briefing_time": datetime.now().isoformat(),
            "current_conditions": current,
            "forecast_6h": forecast_6h,
            "forecast_24h_summary": {
                "avg_wind_speed": sum(f["wind_speed_kts"] for f in forecast_24h) / len(forecast_24h),
                "max_wind_speed": max(f["wind_speed_kts"] for f in forecast_24h),
                "min_visibility": min(f["visibility_km"] for f in forecast_24h),
                "total_precipitation": sum(f["precipitation_mm"] for f in forecast_24h),
            },
            "operational_concerns": concerns,
            "risk_level": self._calculate_risk_level(concerns),
        }

    def _parse_current_weather(self, data: Dict, airport_code: str) -> Dict:
        """Parse current weather data from Open-Meteo response."""
        current = data.get("current", {})

        # Convert m/s to knots if needed (Open-Meteo should return in knots with our param)
        wind_speed_kts = current.get("wind_speed_10m", 0)
        wind_gust_kts = current.get("wind_gusts_10m")

        # Visibility in meters to km
        visibility_m = current.get("visibility", 10000)
        visibility_km = visibility_m / 1000 if visibility_m else 10.0

        # Determine precipitation type based on temperature
        temp_c = current.get("temperature_2m", 15.0)
        precip_mm = current.get("precipitation", 0)

        precipitation_type = "NONE"
        if precip_mm > 0:
            if temp_c < 2:
                precipitation_type = "SNOW"
            elif temp_c < 10:
                precipitation_type = "SLEET"
            else:
                precipitation_type = "RAIN"

        return {
            "airport_code": airport_code,
            "timestamp": datetime.now().isoformat(),
            "temperature_c": temp_c,
            "wind_speed_kts": round(wind_speed_kts, 2),
            "wind_direction_deg": current.get("wind_direction_10m", 0),
            "wind_gust_kts": round(wind_gust_kts, 2) if wind_gust_kts else None,
            "visibility_km": round(visibility_km, 2),
            "cloud_coverage_percent": current.get("cloud_cover", 0),
            "precipitation_type": precipitation_type,
            "precipitation_mm": round(precip_mm, 2),
            "pressure_mb": current.get("surface_pressure", 1013),
            "humidity_percent": current.get("relative_humidity_2m", 50),
            "data_source": "OPEN_METEO",
        }

    def _parse_hourly_forecast(
        self, data: Dict, airport_code: str, max_hours: int
    ) -> List[Dict]:
        """Parse hourly forecast data."""
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])

        forecasts = []
        for i, time_str in enumerate(times[:max_hours]):
            wind_speed = hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else 0
            wind_gust = hourly.get("wind_gusts_10m", [])[i] if i < len(hourly.get("wind_gusts_10m", [])) else None
            visibility = hourly.get("visibility", [])[i] if i < len(hourly.get("visibility", [])) else 10000
            temp = hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else 15
            precip = hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else 0

            # Determine precipitation type
            precipitation_type = "NONE"
            if precip > 0:
                if temp < 2:
                    precipitation_type = "SNOW"
                elif temp < 10:
                    precipitation_type = "SLEET"
                else:
                    precipitation_type = "RAIN"

            forecasts.append({
                "airport_code": airport_code,
                "timestamp": time_str,
                "temperature_c": temp,
                "wind_speed_kts": round(wind_speed, 2),
                "wind_direction_deg": hourly.get("wind_direction_10m", [])[i] if i < len(hourly.get("wind_direction_10m", [])) else 0,
                "wind_gust_kts": round(wind_gust, 2) if wind_gust else None,
                "visibility_km": round(visibility / 1000, 2),
                "cloud_coverage_percent": hourly.get("cloud_cover", [])[i] if i < len(hourly.get("cloud_cover", [])) else 0,
                "precipitation_type": precipitation_type,
                "precipitation_mm": round(precip, 2),
                "precipitation_probability": hourly.get("precipitation_probability", [])[i] if i < len(hourly.get("precipitation_probability", [])) else 0,
                "pressure_mb": hourly.get("surface_pressure", [])[i] if i < len(hourly.get("surface_pressure", [])) else 1013,
                "humidity_percent": hourly.get("relative_humidity_2m", [])[i] if i < len(hourly.get("relative_humidity_2m", [])) else 50,
                "data_source": "OPEN_METEO",
            })

        return forecasts

    def _calculate_risk_level(self, concerns: List[str]) -> str:
        """Calculate operational risk level based on concerns."""
        if not concerns:
            return "LOW"

        severe_concerns = [
            "SEVERE_GUSTS",
            "LOW_VISIBILITY",
            "HEAVY_PRECIPITATION",
        ]

        if any(c in severe_concerns for c in concerns):
            return "HIGH"
        elif len(concerns) >= 3:
            return "MODERATE"
        else:
            return "LOW"


def get_openmeteo_client() -> OpenMeteoClient:
    """Get singleton Open-Meteo client instance."""
    return OpenMeteoClient()


__all__ = ["OpenMeteoError", "OpenMeteoClient", "get_openmeteo_client", "AIRPORT_COORDINATES"]
