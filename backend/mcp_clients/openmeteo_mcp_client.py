"""
Open-Meteo MCP Client

Connects to the open-source Open-Meteo MCP server for weather data.
MCP Server: https://github.com/modelcontextprotocol/servers/tree/main/src/weather

This client uses the MCP protocol to fetch weather data through MCP tools
instead of direct API calls, providing better integration with AI agents.
"""

import os
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class OpenMeteoMCPError(Exception):
    """Exception raised for Open-Meteo MCP client errors."""
    pass


class OpenMeteoMCPClient:
    """
    Client for Open-Meteo MCP Server.
    
    Uses MCP tools to fetch weather data:
    - get_forecast: Get weather forecast for coordinates
    - get_current_weather: Get current weather conditions
    
    Falls back to direct API calls if MCP server is unavailable.
    """
    
    # Major airport coordinates (fallback if MCP unavailable)
    AIRPORT_COORDINATES = {
        "DXB": (25.2532, 55.3657),    # Dubai International
        "LHR": (51.4700, -0.4543),    # London Heathrow
        "JFK": (40.6413, -73.7781),   # New York JFK
        "LAX": (33.9416, -118.4085),  # Los Angeles
        "SIN": (1.3644, 103.9915),    # Singapore Changi
        "FRA": (50.0379, 8.5622),     # Frankfurt
        "NRT": (35.7720, 140.3929),   # Tokyo Narita
        "DEL": (28.5562, 77.1000),    # New Delhi
        "CDG": (49.0097, 2.5479),     # Paris Charles de Gaulle
        "AMS": (52.3105, 4.7683),     # Amsterdam Schiphol
        "HKG": (22.3080, 113.9185),   # Hong Kong
        "SYD": (-33.9399, 151.1753),  # Sydney
        "ORD": (41.9742, -87.9073),   # Chicago O'Hare
        "ATL": (33.6407, -84.4277),   # Atlanta Hartsfield-Jackson
        "DFW": (32.8998, -97.0403),   # Dallas/Fort Worth
    }
    
    def __init__(self, mcp_server_url: Optional[str] = None):
        """
        Initialize Open-Meteo MCP client.
        
        Args:
            mcp_server_url: URL of MCP server (default: http://localhost:3000)
        """
        self.mcp_server_url = mcp_server_url or os.getenv(
            "OPENMETEO_MCP_SERVER_URL",
            "http://localhost:3000"
        )
        self.direct_api_url = "https://api.open-meteo.com/v1/forecast"
        self.use_mcp = self._test_mcp_connection()
        
        if self.use_mcp:
            logger.info(f"Connected to Open-Meteo MCP server at {self.mcp_server_url}")
        else:
            logger.warning("MCP server unavailable, using direct API calls")
    
    def _test_mcp_connection(self) -> bool:
        """Test if MCP server is available."""
        try:
            response = requests.get(
                f"{self.mcp_server_url}/health",
                timeout=2
            )
            return response.status_code == 200
        except Exception:
            return False
    
    def get_airport_coordinates(self, airport_code: str) -> Tuple[float, float]:
        """
        Get coordinates for an airport.
        
        Args:
            airport_code: IATA airport code (e.g., 'DXB', 'LHR')
        
        Returns:
            Tuple of (latitude, longitude)
        
        Raises:
            OpenMeteoMCPError: If airport code is not supported
        """
        airport_code = airport_code.upper()
        if airport_code not in self.AIRPORT_COORDINATES:
            raise OpenMeteoMCPError(
                f"Airport {airport_code} not supported. "
                f"Supported: {', '.join(self.AIRPORT_COORDINATES.keys())}"
            )
        return self.AIRPORT_COORDINATES[airport_code]
    
    def get_current_weather(self, airport_code: str) -> Dict:
        """
        Get current weather for an airport using MCP tools.
        
        Args:
            airport_code: IATA airport code
        
        Returns:
            Dict with current weather data
        """
        lat, lng = self.get_airport_coordinates(airport_code)
        
        if self.use_mcp:
            return self._get_current_weather_mcp(lat, lng, airport_code)
        else:
            return self._get_current_weather_direct(lat, lng, airport_code)
    
    def _get_current_weather_mcp(
        self,
        latitude: float,
        longitude: float,
        airport_code: str
    ) -> Dict:
        """Fetch current weather via MCP server."""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/call-tool",
                json={
                    "name": "get_forecast",
                    "arguments": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "forecast_days": 1
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                raise OpenMeteoMCPError(f"MCP server error: {response.status_code}")
            
            data = response.json()
            return self._parse_mcp_current_weather(data, airport_code)
            
        except Exception as e:
            logger.error(f"MCP call failed: {e}, falling back to direct API")
            return self._get_current_weather_direct(latitude, longitude, airport_code)
    
    def _get_current_weather_direct(
        self,
        latitude: float,
        longitude: float,
        airport_code: str
    ) -> Dict:
        """Fetch current weather via direct API (fallback)."""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "weather_code",
                    "cloud_cover",
                    "pressure_msl",
                    "wind_speed_10m",
                    "wind_direction_10m",
                    "wind_gusts_10m"
                ],
                "temperature_unit": "celsius",
                "wind_speed_unit": "kn",
                "precipitation_unit": "mm"
            }
            
            response = requests.get(self.direct_api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_current_weather(data, airport_code)
            
        except Exception as e:
            raise OpenMeteoMCPError(f"Failed to fetch weather: {str(e)}")
    
    def _parse_current_weather(self, data: Dict, airport_code: str) -> Dict:
        """Parse Open-Meteo API response."""
        current = data.get("current", {})
        
        # Calculate visibility from weather code
        weather_code = current.get("weather_code", 0)
        visibility_km = self._weather_code_to_visibility(weather_code)
        
        # Determine precipitation type
        precip_mm = current.get("precipitation", 0.0)
        temp_c = current.get("temperature_2m", 15.0)
        precipitation_type = self._determine_precipitation_type(precip_mm, temp_c)
        
        return {
            "airport_code": airport_code.upper(),
            "timestamp": datetime.now().isoformat(),
            "temperature_c": current.get("temperature_2m", 0.0),
            "wind_speed_kts": current.get("wind_speed_10m", 0.0),
            "wind_direction_deg": current.get("wind_direction_10m", 0),
            "wind_gust_kts": current.get("wind_gusts_10m", 0.0),
            "visibility_km": visibility_km,
            "cloud_coverage_percent": current.get("cloud_cover", 0),
            "precipitation_type": precipitation_type,
            "precipitation_mm": precip_mm,
            "pressure_mb": current.get("pressure_msl", 1013.0),
            "humidity_percent": current.get("relative_humidity_2m", 50),
            "data_source": "OPENMETEO_MCP" if self.use_mcp else "OPENMETEO_DIRECT"
        }
    
    def _parse_mcp_current_weather(self, data: Dict, airport_code: str) -> Dict:
        """Parse MCP server response."""
        # MCP server returns weather data in result field
        result = data.get("result", {})
        current = result.get("current", {})
        
        return self._parse_current_weather({"current": current}, airport_code)
    
    def get_hourly_forecast(
        self,
        airport_code: str,
        hours: int = 48
    ) -> List[Dict]:
        """
        Get hourly forecast for an airport.
        
        Args:
            airport_code: IATA airport code
            hours: Number of forecast hours (1-168)
        
        Returns:
            List of hourly forecast dicts
        """
        if hours < 1 or hours > 168:
            raise ValueError("Hours must be between 1 and 168")
        
        lat, lng = self.get_airport_coordinates(airport_code)
        
        if self.use_mcp:
            return self._get_hourly_forecast_mcp(lat, lng, airport_code, hours)
        else:
            return self._get_hourly_forecast_direct(lat, lng, airport_code, hours)
    
    def _get_hourly_forecast_mcp(
        self,
        latitude: float,
        longitude: float,
        airport_code: str,
        hours: int
    ) -> List[Dict]:
        """Fetch hourly forecast via MCP server."""
        try:
            forecast_days = (hours + 23) // 24  # Round up to nearest day
            
            response = requests.post(
                f"{self.mcp_server_url}/call-tool",
                json={
                    "name": "get_forecast",
                    "arguments": {
                        "latitude": latitude,
                        "longitude": longitude,
                        "forecast_days": min(forecast_days, 7)
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                raise OpenMeteoMCPError(f"MCP server error: {response.status_code}")
            
            data = response.json()
            return self._parse_mcp_hourly_forecast(data, airport_code, hours)
            
        except Exception as e:
            logger.error(f"MCP call failed: {e}, falling back to direct API")
            return self._get_hourly_forecast_direct(latitude, longitude, airport_code, hours)
    
    def _get_hourly_forecast_direct(
        self,
        latitude: float,
        longitude: float,
        airport_code: str,
        hours: int
    ) -> List[Dict]:
        """Fetch hourly forecast via direct API (fallback)."""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "hourly": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "precipitation",
                    "weather_code",
                    "cloud_cover",
                    "wind_speed_10m",
                    "wind_direction_10m",
                ],
                "temperature_unit": "celsius",
                "wind_speed_unit": "kn",
                "precipitation_unit": "mm",
                "forecast_days": min((hours + 23) // 24, 7)
            }
            
            response = requests.get(self.direct_api_url, params=params, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            return self._parse_hourly_forecast(data, airport_code, hours)
            
        except Exception as e:
            raise OpenMeteoMCPError(f"Failed to fetch forecast: {str(e)}")
    
    def _parse_hourly_forecast(
        self,
        data: Dict,
        airport_code: str,
        hours: int
    ) -> List[Dict]:
        """Parse hourly forecast from API response."""
        hourly = data.get("hourly", {})
        times = hourly.get("time", [])
        
        forecasts = []
        for i in range(min(hours, len(times))):
            weather_code = hourly.get("weather_code", [])[i] if i < len(hourly.get("weather_code", [])) else 0
            visibility_km = self._weather_code_to_visibility(weather_code)
            
            precip_mm = hourly.get("precipitation", [])[i] if i < len(hourly.get("precipitation", [])) else 0.0
            temp_c = hourly.get("temperature_2m", [])[i] if i < len(hourly.get("temperature_2m", [])) else 15.0
            precipitation_type = self._determine_precipitation_type(precip_mm, temp_c)
            
            forecasts.append({
                "airport_code": airport_code.upper(),
                "timestamp": times[i],
                "temperature_c": temp_c,
                "wind_speed_kts": hourly.get("wind_speed_10m", [])[i] if i < len(hourly.get("wind_speed_10m", [])) else 0.0,
                "wind_direction_deg": hourly.get("wind_direction_10m", [])[i] if i < len(hourly.get("wind_direction_10m", [])) else 0,
                "visibility_km": visibility_km,
                "cloud_coverage_percent": hourly.get("cloud_cover", [])[i] if i < len(hourly.get("cloud_cover", [])) else 0,
                "precipitation_type": precipitation_type,
                "precipitation_mm": precip_mm,
                "humidity_percent": hourly.get("relative_humidity_2m", [])[i] if i < len(hourly.get("relative_humidity_2m", [])) else 50,
            })
        
        return forecasts
    
    def _parse_mcp_hourly_forecast(
        self,
        data: Dict,
        airport_code: str,
        hours: int
    ) -> List[Dict]:
        """Parse MCP server forecast response."""
        result = data.get("result", {})
        hourly = result.get("hourly", {})
        
        return self._parse_hourly_forecast({"hourly": hourly}, airport_code, hours)
    
    def get_weather_at_time(
        self,
        airport_code: str,
        target_time: datetime
    ) -> Dict:
        """
        Get weather forecast at a specific time.
        
        Args:
            airport_code: IATA airport code
            target_time: Target datetime
        
        Returns:
            Dict with weather data at target time
        """
        hours_ahead = int((target_time - datetime.now()).total_seconds() / 3600)
        
        if hours_ahead < 0:
            raise ValueError("Cannot forecast past weather")
        if hours_ahead > 168:
            raise ValueError("Forecast limited to 7 days (168 hours)")
        
        # Get hourly forecast up to target time
        forecast = self.get_hourly_forecast(airport_code, hours_ahead + 1)
        
        # Find closest forecast to target time
        if not forecast:
            raise OpenMeteoMCPError("No forecast data available")
        
        return forecast[-1]  # Return last (closest to target) forecast
    
    def get_aviation_weather_briefing(self, airport_code: str) -> Dict:
        """
        Get comprehensive aviation weather briefing.
        
        Args:
            airport_code: IATA airport code
        
        Returns:
            Dict with aviation weather briefing
        """
        current = self.get_current_weather(airport_code)
        forecast_24h = self.get_hourly_forecast(airport_code, 24)
        
        # Analyze conditions
        concerns = []
        if current["wind_speed_kts"] > 25:
            concerns.append("Strong winds")
        if current["wind_gust_kts"] > 35:
            concerns.append("Strong gusts")
        if current["visibility_km"] < 5:
            concerns.append("Reduced visibility")
        if current["precipitation_mm"] > 5:
            concerns.append("Heavy precipitation")
        if current["cloud_coverage_percent"] > 75:
            concerns.append("Low ceiling expected")
        
        # Find worst conditions in next 24 hours
        max_wind = max([f["wind_speed_kts"] for f in forecast_24h])
        min_visibility = min([f["visibility_km"] for f in forecast_24h])
        max_precip = max([f["precipitation_mm"] for f in forecast_24h])
        
        risk_level = self._calculate_risk_level(concerns)
        
        return {
            "airport_code": airport_code.upper(),
            "briefing_time": datetime.now().isoformat(),
            "current_conditions": current,
            "forecast_24h_summary": {
                "max_wind_speed_kts": max_wind,
                "min_visibility_km": min_visibility,
                "max_precipitation_mm": max_precip,
            },
            "operational_concerns": concerns,
            "risk_level": risk_level,
            "recommendation": self._get_recommendation(risk_level),
            "data_source": "OPENMETEO_MCP" if self.use_mcp else "OPENMETEO_DIRECT"
        }
    
    def _weather_code_to_visibility(self, code: int) -> float:
        """Convert WMO weather code to visibility estimate in km."""
        if code == 0:
            return 10.0  # Clear
        elif code in [1, 2]:
            return 8.0  # Mainly clear
        elif code == 3:
            return 7.0  # Overcast
        elif code in [45, 48]:
            return 1.0  # Fog
        elif code in [51, 53, 55, 56, 57]:
            return 5.0  # Drizzle
        elif code in [61, 63, 65, 66, 67]:
            return 3.0  # Rain
        elif code in [71, 73, 75, 77]:
            return 2.0  # Snow
        elif code in [80, 81, 82]:
            return 4.0  # Rain showers
        elif code in [85, 86]:
            return 2.0  # Snow showers
        elif code in [95, 96, 99]:
            return 2.0  # Thunderstorm
        else:
            return 6.0  # Default
    
    def _determine_precipitation_type(self, precip_mm: float, temp_c: float) -> str:
        """Determine precipitation type based on amount and temperature."""
        if precip_mm < 0.1:
            return "NONE"
        elif temp_c < 0:
            return "SNOW"
        elif temp_c < 2:
            return "SLEET"
        elif precip_mm < 2.5:
            return "LIGHT_RAIN"
        elif precip_mm < 7.5:
            return "MODERATE_RAIN"
        else:
            return "HEAVY_RAIN"
    
    def _calculate_risk_level(self, concerns: List[str]) -> str:
        """Calculate operational risk level based on concerns."""
        if len(concerns) == 0:
            return "LOW"
        elif len(concerns) <= 2:
            return "MODERATE"
        elif len(concerns) <= 3:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _get_recommendation(self, risk_level: str) -> str:
        """Get operational recommendation based on risk level."""
        recommendations = {
            "LOW": "Normal operations expected",
            "MODERATE": "Monitor conditions, minor delays possible",
            "HIGH": "Expect delays, consider alternate airports",
            "CRITICAL": "Severe disruptions expected, divert if possible"
        }
        return recommendations.get(risk_level, "Unknown risk level")


def get_openmeteo_mcp_client() -> OpenMeteoMCPClient:
    """Get singleton instance of Open-Meteo MCP client."""
    return OpenMeteoMCPClient()
