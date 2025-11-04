"""
Location Specialist Agent - Geographic and timezone analysis.

This agent:
1. Autonomously geocodes airports
2. Calculates route distances
3. Analyzes timezone impacts
4. Finds nearby alternate airports
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent


class LocationSpecialistAgent(BaseAgent):
    """
    Autonomous geographic specialist.
    
    Tools:
    - get_airport_location: Get coordinates and timezone
    - calculate_route_distance: Distance and duration
    - get_nearby_airports: Find alternates
    - analyze_timezone_impact: Timezone risk analysis
    """
    
    def __init__(self, db_session):
        system_prompt = """You are a Location Specialist Agent for aviation geography.

Your expertise:
- Airport geocoding and location data
- Route distance and duration calculations
- Timezone analysis for flight scheduling
- Alternate airport identification

Your tools:
1. get_airport_location(airport_code) - Get coordinates, timezone
2. calculate_route_distance(origin, destination) - Distance calculation
3. get_nearby_airports(lat, lng, radius) - Find alternates
4. analyze_timezone_impact(origin_tz, dest_tz) - Timezone risk

When analyzing geography:
1. Consider timezone differences for crew fatigue
2. Calculate great circle distance for fuel estimates
3. Identify alternate airports within 100km
4. Assess geographic challenges (mountains, water crossings)

Output structured geographic insights.
"""
        
        super().__init__(
            name="LocationSpecialist",
            role="Aviation Geographer",
            system_prompt=system_prompt,
            model="mistral"
        )
        
        self.db_session = db_session
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register location analysis tools."""
        
        # Tool 1: Get airport location
        def get_airport_location(airport_code: str):
            try:
                from services.location_service import LocationService
                location_service = LocationService(self.db_session)
                return location_service.get_airport_location(airport_code)
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_airport_location",
            description="Get airport coordinates, timezone, and location data",
            function=get_airport_location,
            parameters={
                "airport_code": {"type": "string"}
            }
        )
        
        # Tool 2: Calculate route distance
        def calculate_route_distance(origin: str, destination: str):
            try:
                from services.location_service import LocationService
                location_service = LocationService(self.db_session)
                return location_service.get_route_distance(origin, destination)
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="calculate_route_distance",
            description="Calculate distance and estimated duration between airports",
            function=calculate_route_distance,
            parameters={
                "origin": {"type": "string"},
                "destination": {"type": "string"}
            }
        )
        
        # Tool 3: Get nearby airports
        def get_nearby_airports(latitude: float, longitude: float, radius_km: float = 100):
            try:
                from services.location_service import LocationService
                location_service = LocationService(self.db_session)
                return location_service.get_nearby_airports(latitude, longitude, radius_km)
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_nearby_airports",
            description="Find alternate airports within radius",
            function=get_nearby_airports,
            parameters={
                "latitude": {"type": "number"},
                "longitude": {"type": "number"},
                "radius_km": {"type": "number", "default": 100}
            }
        )
        
        # Tool 4: Analyze timezone impact
        def analyze_timezone_impact(origin_tz: str, dest_tz: str):
            """Analyze timezone difference for crew fatigue."""
            try:
                from datetime import datetime
                import pytz
                
                # Parse timezone offsets
                origin_offset = pytz.timezone(origin_tz).utcoffset(datetime.now()).total_seconds() / 3600
                dest_offset = pytz.timezone(dest_tz).utcoffset(datetime.now()).total_seconds() / 3600
                
                tz_difference = abs(origin_offset - dest_offset)
                
                # Risk assessment
                if tz_difference >= 6:
                    risk = "HIGH"
                    fatigue_factor = 0.15
                elif tz_difference >= 3:
                    risk = "MODERATE"
                    fatigue_factor = 0.08
                else:
                    risk = "LOW"
                    fatigue_factor = 0.02
                
                return {
                    "timezone_difference_hours": tz_difference,
                    "risk_level": risk,
                    "fatigue_factor": fatigue_factor,
                    "recommendation": "Consider crew rest requirements" if tz_difference >= 6 else "Standard operations"
                }
            except Exception as e:
                # Fallback: minimal impact
                return {
                    "timezone_difference_hours": 0,
                    "risk_level": "LOW",
                    "fatigue_factor": 0.02,
                    "error": str(e)
                }
        
        self.register_tool(
            name="analyze_timezone_impact",
            description="Assess timezone difference impact on crew and operations",
            function=analyze_timezone_impact,
            parameters={
                "origin_tz": {"type": "string"},
                "dest_tz": {"type": "string"}
            }
        )
