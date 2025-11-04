"""
Flight Specialist Agent - Historical flight pattern analysis.

This agent:
1. Autonomously fetches historical flight data
2. Analyzes route-specific delay patterns
3. Identifies temporal patterns (day of week, time of day)
4. Calculates route reliability metrics
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.base_agent import BaseAgent
from external_apis.flight_tracking import AviationStackClient


class FlightSpecialistAgent(BaseAgent):
    """
    Autonomous flight history specialist.
    
    Tools:
    - get_route_history: Fetch historical route data
    - calculate_route_stats: Calculate delay statistics
    - analyze_temporal_patterns: Day/time analysis
    - get_real_time_flights: Current flight status
    """
    
    def __init__(self):
        system_prompt = """You are a Flight Operations Specialist Agent.

Your expertise:
- Historical flight performance analysis
- Route reliability assessment
- Temporal pattern recognition (day of week, time of day, seasonality)
- Airline operational patterns

Your tools:
1. get_route_history(origin, destination, days) - Historical route data
2. calculate_route_stats(route_data) - Statistical analysis
3. analyze_temporal_patterns(route_data) - Pattern recognition
4. get_real_time_flights(flight_iata) - Current status

When analyzing flights:
1. Look at 30-90 day history for patterns
2. Identify consistent delay factors
3. Consider airline-specific performance
4. Weight recent data more heavily
5. Account for seasonality

Output structured insights with statistical confidence.
"""
        
        super().__init__(
            name="FlightSpecialist",
            role="Aviation Operations Analyst",
            system_prompt=system_prompt,
            model="mistral"
        )
        
        # Initialize flight tracking client
        self.flight_client = AviationStackClient()
        
        # Register tools
        self._register_tools()
    
    def _register_tools(self):
        """Register flight analysis tools."""
        
        # Tool 1: Get route history
        def get_route_history(origin: str, destination: str, days: int = 30):
            try:
                history = self.flight_client.get_flight_route_history(
                    dep_iata=origin,
                    arr_iata=destination,
                    days_back=days
                )
                return history if history else {"error": "No route history found"}
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_route_history",
            description="Get historical flight data for a route",
            function=get_route_history,
            parameters={
                "origin": {"type": "string"},
                "destination": {"type": "string"},
                "days": {"type": "integer", "default": 30}
            }
        )
        
        # Tool 2: Calculate route statistics
        def calculate_route_stats(route_data: list):
            try:
                if not route_data:
                    return {"error": "No data provided"}
                
                stats = self.flight_client.calculate_route_statistics(route_data)
                return stats
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="calculate_route_stats",
            description="Calculate statistical metrics for route performance",
            function=calculate_route_stats,
            parameters={
                "route_data": {"type": "array"}
            }
        )
        
        # Tool 3: Analyze temporal patterns
        def analyze_temporal_patterns(route_data: list):
            """Analyze day-of-week and time-of-day patterns."""
            try:
                from datetime import datetime
                from collections import defaultdict
                
                if not route_data:
                    return {"error": "No data provided"}
                
                # Group by day of week
                day_delays = defaultdict(list)
                hour_delays = defaultdict(list)
                
                for flight in route_data:
                    if flight.get("delay_minutes") and flight.get("departure_time"):
                        delay = flight["delay_minutes"]
                        dt = datetime.fromisoformat(flight["departure_time"].replace("Z", "+00:00"))
                        
                        day_delays[dt.strftime("%A")].append(delay)
                        hour_delays[dt.hour].append(delay)
                
                # Calculate averages
                day_avg = {
                    day: sum(delays) / len(delays)
                    for day, delays in day_delays.items()
                }
                
                hour_avg = {
                    hour: sum(delays) / len(delays)
                    for hour, delays in hour_delays.items()
                }
                
                # Find worst times
                worst_day = max(day_avg, key=day_avg.get) if day_avg else None
                worst_hour = max(hour_avg, key=hour_avg.get) if hour_avg else None
                
                return {
                    "day_of_week_patterns": day_avg,
                    "hour_of_day_patterns": {str(k): v for k, v in hour_avg.items()},
                    "worst_day": worst_day,
                    "worst_hour": worst_hour,
                    "temporal_risk_factor": 0.15 if worst_day or worst_hour else 0.05
                }
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="analyze_temporal_patterns",
            description="Identify day-of-week and time-of-day delay patterns",
            function=analyze_temporal_patterns,
            parameters={
                "route_data": {"type": "array"}
            }
        )
        
        # Tool 4: Get real-time status
        def get_real_time_flights(flight_iata: str = None, dep_iata: str = None):
            try:
                flights = self.flight_client.get_real_time_flights(
                    flight_iata=flight_iata,
                    dep_iata=dep_iata,
                    limit=10
                )
                return flights if flights else {"error": "No flights found"}
            except Exception as e:
                return {"error": str(e)}
        
        self.register_tool(
            name="get_real_time_flights",
            description="Get current real-time flight status",
            function=get_real_time_flights,
            parameters={
                "flight_iata": {"type": "string", "optional": True},
                "dep_iata": {"type": "string", "optional": True}
            }
        )
