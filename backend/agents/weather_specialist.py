"""
Weather Specialist Agent - Autonomous weather analysis for aviation.

This agent:
1. Autonomously fetches weather data
2. Analyzes aviation-specific risks (crosswind, visibility, icing)
3. Predicts weather impact on flight delays
4. Makes recommendations
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from external_apis.openmeteo_weather import OpenMeteoClient


class WeatherSpecialistAgent(BaseAgent):
    """
    Autonomous weather specialist for flight predictions.
    
    Tools:
    - get_current_weather: Fetch current conditions
    - get_forecast: Get hourly forecast
    - get_aviation_briefing: Get aviation-specific briefing
    - analyze_weather_trends: Identify patterns
    """
    
    def __init__(self):
        system_prompt = """You are a Weather Specialist Agent for aviation operations.

Your expertise:
- Meteorological analysis for flight operations
- Aviation weather hazards (crosswind, visibility, icing, turbulence)
- Weather trend analysis and forecasting
- Risk assessment for flight safety

Your tools:
1. get_current_weather(airport_code) - Current conditions
2. get_forecast(airport_code, hours) - Hourly forecast
3. get_aviation_briefing(airport_code) - Full briefing
4. analyze_weather_trends(data) - Pattern recognition

When analyzing weather:
1. Check conditions at origin AND destination
2. Consider forecast at scheduled departure time
3. Assess aviation-specific risks (not just general weather)
4. Quantify impact on delay probability

Output insights in JSON format with risk scores.
"""
        
        super().__init__(
            name="WeatherSpecialist",
            role="Aviation Meteorologist",
            system_prompt=system_prompt,
            model="mistral"
        )
        
        # Initialize weather API client
        self.weather_client = OpenMeteoClient()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register weather analysis tools."""
        
        # Tool 1: Get current weather
        def get_current_weather(airport_code: str):
            try:
                return self.weather_client.get_current_weather(airport_code)
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_current_weather",
            description="Get current weather conditions at an airport",
            function=get_current_weather,
            parameters={
                "airport_code": {
                    "type": "string",
                    "description": "IATA airport code (e.g., 'DXB', 'LHR')"
                }
            }
        )
        
        # Tool 2: Get forecast
        def get_forecast(airport_code: str, hours: int = 24):
            try:
                return self.weather_client.get_hourly_forecast(airport_code, hours)
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_forecast",
            description="Get hourly weather forecast for airport",
            function=get_forecast,
            parameters={
                "airport_code": {"type": "string"},
                "hours": {"type": "integer", "default": 24}
            }
        )
        
        # Tool 3: Get aviation briefing
        def get_aviation_briefing(airport_code: str):
            try:
                return self.weather_client.get_aviation_weather_briefing(airport_code)
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_aviation_briefing",
            description="Get comprehensive aviation weather briefing",
            function=get_aviation_briefing,
            parameters={
                "airport_code": {"type": "string"}
            }
        )
        
        # Tool 4: Analyze trends
        def analyze_weather_trends(weather_data: dict):
            """Analyze weather patterns for delay correlation."""
            try:
                # Extract key metrics
                wind = weather_data.get("wind_speed_kts", 0)
                visibility = weather_data.get("visibility_km", 10)
                precip = weather_data.get("precipitation_mm", 0)
                
                # Risk scoring
                wind_risk = min(wind / 30, 1.0)  # >30kts = high risk
                visibility_risk = max(0, (10 - visibility) / 10)
                precip_risk = min(precip / 10, 1.0)
                
                overall_risk = (wind_risk + visibility_risk + precip_risk) / 3
                
                return {
                    "risk_scores": {
                        "wind": round(wind_risk, 2),
                        "visibility": round(visibility_risk, 2),
                        "precipitation": round(precip_risk, 2),
                        "overall": round(overall_risk, 2)
                    },
                    "delay_contribution": round(overall_risk * 0.3, 2),  # Max 30% contribution
                    "severity": "HIGH" if overall_risk > 0.7 else "MODERATE" if overall_risk > 0.4 else "LOW"
                }
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="analyze_weather_trends",
            description="Analyze weather data and calculate risk scores",
            function=analyze_weather_trends,
            parameters={
                "weather_data": {"type": "object"}
            }
        )
