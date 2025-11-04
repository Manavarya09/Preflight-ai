"""
AviationStack MCP Client

Connects to the AviationStack MCP server adapter for real-time flight tracking.
This MCP server acts as an adapter to the AviationStack API.

Falls back to direct API calls if MCP server is unavailable.
"""

import os
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import requests

logger = logging.getLogger(__name__)


class AviationStackMCPError(Exception):
    """Exception raised for AviationStack MCP client errors."""
    pass


class AviationStackMCPClient:
    """
    Client for AviationStack MCP Server.
    
    Uses MCP tools to fetch flight data:
    - get_real_time_flights: Get live flight information
    - get_historical_flights: Get historical flight data
    - get_route_info: Get route information
    
    Falls back to direct API calls if MCP server is unavailable.
    """
    
    def __init__(
        self,
        mcp_server_url: Optional[str] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize AviationStack MCP client.
        
        Args:
            mcp_server_url: URL of MCP server (default: http://localhost:3001)
            api_key: AviationStack API key (for fallback)
        """
        self.mcp_server_url = mcp_server_url or os.getenv(
            "AVIATIONSTACK_MCP_SERVER_URL",
            "http://localhost:3001"
        )
        self.api_key = api_key or os.getenv("AVIATIONSTACK_API_KEY")
        self.base_url = "https://api.aviationstack.com/v1"
        self.use_mcp = self._test_mcp_connection()
        
        if not self.api_key and not self.use_mcp:
            logger.warning("No AviationStack API key and MCP server unavailable")
        
        if self.use_mcp:
            logger.info(f"Connected to AviationStack MCP server at {self.mcp_server_url}")
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
    
    def get_real_time_flights(
        self,
        flight_iata: Optional[str] = None,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Get real-time flight information using MCP tools.
        
        Args:
            flight_iata: Flight IATA code (e.g., 'EK230')
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            limit: Maximum number of results (1-100)
        
        Returns:
            List of flight dicts
        """
        if limit < 1 or limit > 100:
            raise ValueError("Limit must be between 1 and 100")
        
        if self.use_mcp:
            return self._get_real_time_flights_mcp(
                flight_iata, dep_iata, arr_iata, limit
            )
        else:
            return self._get_real_time_flights_direct(
                flight_iata, dep_iata, arr_iata, limit
            )
    
    def _get_real_time_flights_mcp(
        self,
        flight_iata: Optional[str],
        dep_iata: Optional[str],
        arr_iata: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Fetch real-time flights via MCP server."""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/call-tool",
                json={
                    "name": "get_real_time_flights",
                    "arguments": {
                        "flight_iata": flight_iata,
                        "dep_iata": dep_iata,
                        "arr_iata": arr_iata,
                        "limit": limit
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                raise AviationStackMCPError(f"MCP server error: {response.status_code}")
            
            data = response.json()
            result = data.get("result", {})
            flights = result.get("data", [])
            
            return self._parse_flight_data(flights)
            
        except Exception as e:
            logger.error(f"MCP call failed: {e}, falling back to direct API")
            return self._get_real_time_flights_direct(
                flight_iata, dep_iata, arr_iata, limit
            )
    
    def _get_real_time_flights_direct(
        self,
        flight_iata: Optional[str],
        dep_iata: Optional[str],
        arr_iata: Optional[str],
        limit: int
    ) -> List[Dict]:
        """Fetch real-time flights via direct API (fallback)."""
        if not self.api_key:
            raise AviationStackMCPError("No API key available and MCP server unavailable")
        
        try:
            params = {
                "access_key": self.api_key,
                "limit": limit
            }
            
            if flight_iata:
                params["flight_iata"] = flight_iata
            if dep_iata:
                params["dep_iata"] = dep_iata
            if arr_iata:
                params["arr_iata"] = arr_iata
            
            response = requests.get(
                f"{self.base_url}/flights",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            flights = data.get("data", [])
            
            return self._parse_flight_data(flights)
            
        except Exception as e:
            raise AviationStackMCPError(f"Failed to fetch flights: {str(e)}")
    
    def get_historical_flights(
        self,
        flight_date: str,
        flight_iata: Optional[str] = None,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None
    ) -> List[Dict]:
        """
        Get historical flight information using MCP tools.
        
        Args:
            flight_date: Flight date in YYYY-MM-DD format
            flight_iata: Flight IATA code
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
        
        Returns:
            List of historical flight dicts
        """
        # Validate date format
        try:
            datetime.strptime(flight_date, "%Y-%m-%d")
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
        
        if self.use_mcp:
            return self._get_historical_flights_mcp(
                flight_date, flight_iata, dep_iata, arr_iata
            )
        else:
            return self._get_historical_flights_direct(
                flight_date, flight_iata, dep_iata, arr_iata
            )
    
    def _get_historical_flights_mcp(
        self,
        flight_date: str,
        flight_iata: Optional[str],
        dep_iata: Optional[str],
        arr_iata: Optional[str]
    ) -> List[Dict]:
        """Fetch historical flights via MCP server."""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/call-tool",
                json={
                    "name": "get_historical_flights",
                    "arguments": {
                        "flight_date": flight_date,
                        "flight_iata": flight_iata,
                        "dep_iata": dep_iata,
                        "arr_iata": arr_iata
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                raise AviationStackMCPError(f"MCP server error: {response.status_code}")
            
            data = response.json()
            result = data.get("result", {})
            flights = result.get("data", [])
            
            return self._parse_flight_data(flights)
            
        except Exception as e:
            logger.error(f"MCP call failed: {e}, falling back to direct API")
            return self._get_historical_flights_direct(
                flight_date, flight_iata, dep_iata, arr_iata
            )
    
    def _get_historical_flights_direct(
        self,
        flight_date: str,
        flight_iata: Optional[str],
        dep_iata: Optional[str],
        arr_iata: Optional[str]
    ) -> List[Dict]:
        """Fetch historical flights via direct API (fallback)."""
        if not self.api_key:
            raise AviationStackMCPError("No API key available and MCP server unavailable")
        
        try:
            params = {
                "access_key": self.api_key,
                "flight_date": flight_date,
                "limit": 100
            }
            
            if flight_iata:
                params["flight_iata"] = flight_iata
            if dep_iata:
                params["dep_iata"] = dep_iata
            if arr_iata:
                params["arr_iata"] = arr_iata
            
            response = requests.get(
                f"{self.base_url}/flights",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            flights = data.get("data", [])
            
            return self._parse_flight_data(flights)
            
        except Exception as e:
            raise AviationStackMCPError(f"Failed to fetch historical flights: {str(e)}")
    
    def get_flight_route_history(
        self,
        dep_iata: str,
        arr_iata: str,
        days_back: int = 30
    ) -> List[Dict]:
        """
        Get historical data for a flight route.
        
        Args:
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            days_back: Number of days to look back (1-90)
        
        Returns:
            List of historical flight dicts
        """
        if days_back < 1 or days_back > 90:
            raise ValueError("Days back must be between 1 and 90")
        
        all_flights = []
        current_date = datetime.now()
        
        # Query flights for each day in the range
        for i in range(days_back):
            date = current_date - timedelta(days=i)
            date_str = date.strftime("%Y-%m-%d")
            
            try:
                flights = self.get_historical_flights(
                    flight_date=date_str,
                    dep_iata=dep_iata,
                    arr_iata=arr_iata
                )
                all_flights.extend(flights)
            except Exception as e:
                logger.warning(f"Failed to fetch flights for {date_str}: {e}")
                continue
        
        return all_flights
    
    def calculate_route_statistics(self, route_history: List[Dict]) -> Dict:
        """
        Calculate statistics for a flight route.
        
        Args:
            route_history: List of historical flight dicts
        
        Returns:
            Dict with route statistics
        """
        if not route_history:
            return {
                "error": "No flight data available",
                "statistics": {}
            }
        
        total_flights = len(route_history)
        delays = [f["delay_minutes"] for f in route_history if f.get("delay_minutes") is not None]
        on_time_flights = sum(1 for d in delays if d <= 15)
        delayed_flights = sum(1 for d in delays if d > 15)
        
        avg_delay = sum(delays) / len(delays) if delays else 0
        max_delay = max(delays) if delays else 0
        
        on_time_percentage = (on_time_flights / len(delays) * 100) if delays else 0
        delay_percentage = (delayed_flights / len(delays) * 100) if delays else 0
        
        return {
            "route": f"{route_history[0].get('departure_airport')} → {route_history[0].get('arrival_airport')}",
            "total_flights": total_flights,
            "statistics": {
                "avg_delay_minutes": round(avg_delay, 2),
                "max_delay_minutes": max_delay,
                "on_time_percentage": round(on_time_percentage, 2),
                "delay_percentage": round(delay_percentage, 2),
                "total_delayed": delayed_flights,
                "total_on_time": on_time_flights
            }
        }
    
    def get_airport_info(self, airport_iata: str) -> Dict:
        """
        Get airport information using MCP tools.
        
        Args:
            airport_iata: Airport IATA code
        
        Returns:
            Dict with airport information
        """
        if self.use_mcp:
            return self._get_airport_info_mcp(airport_iata)
        else:
            return self._get_airport_info_direct(airport_iata)
    
    def _get_airport_info_mcp(self, airport_iata: str) -> Dict:
        """Fetch airport info via MCP server."""
        try:
            response = requests.post(
                f"{self.mcp_server_url}/call-tool",
                json={
                    "name": "get_airport_info",
                    "arguments": {
                        "airport_iata": airport_iata
                    }
                },
                timeout=15
            )
            
            if response.status_code != 200:
                raise AviationStackMCPError(f"MCP server error: {response.status_code}")
            
            data = response.json()
            return data.get("result", {})
            
        except Exception as e:
            logger.error(f"MCP call failed: {e}, falling back to direct API")
            return self._get_airport_info_direct(airport_iata)
    
    def _get_airport_info_direct(self, airport_iata: str) -> Dict:
        """Fetch airport info via direct API (fallback)."""
        if not self.api_key:
            raise AviationStackMCPError("No API key available and MCP server unavailable")
        
        try:
            params = {
                "access_key": self.api_key,
                "search": airport_iata
            }
            
            response = requests.get(
                f"{self.base_url}/airports",
                params=params,
                timeout=15
            )
            response.raise_for_status()
            
            data = response.json()
            airports = data.get("data", [])
            
            if not airports:
                raise AviationStackMCPError(f"Airport {airport_iata} not found")
            
            return airports[0]
            
        except Exception as e:
            raise AviationStackMCPError(f"Failed to fetch airport info: {str(e)}")
    
    def _parse_flight_data(self, flights: List[Dict]) -> List[Dict]:
        """
        Parse and standardize flight data.
        
        Args:
            flights: Raw flight data from API
        
        Returns:
            List of parsed flight dicts
        """
        parsed_flights = []
        
        for flight in flights:
            try:
                # Extract key information
                flight_info = flight.get("flight", {})
                departure = flight.get("departure", {})
                arrival = flight.get("arrival", {})
                
                # Calculate delay if both scheduled and actual times available
                delay_minutes = None
                if departure.get("scheduled") and departure.get("actual"):
                    try:
                        scheduled = datetime.fromisoformat(
                            departure["scheduled"].replace("Z", "+00:00")
                        )
                        actual = datetime.fromisoformat(
                            departure["actual"].replace("Z", "+00:00")
                        )
                        delay_minutes = int((actual - scheduled).total_seconds() / 60)
                    except Exception as e:
                        logger.debug(f"Failed to calculate delay: {e}")
                
                parsed_flights.append({
                    "flight_number": flight_info.get("iata", "UNKNOWN"),
                    "airline": flight.get("airline", {}).get("name", "Unknown"),
                    "departure_airport": departure.get("iata", "UNKNOWN"),
                    "arrival_airport": arrival.get("iata", "UNKNOWN"),
                    "scheduled_departure": departure.get("scheduled"),
                    "actual_departure": departure.get("actual"),
                    "scheduled_arrival": arrival.get("scheduled"),
                    "actual_arrival": arrival.get("actual"),
                    "flight_status": flight.get("flight_status", "unknown"),
                    "delay_minutes": delay_minutes,
                    "terminal": departure.get("terminal"),
                    "gate": departure.get("gate"),
                    "data_source": "AVIATIONSTACK_MCP" if self.use_mcp else "AVIATIONSTACK_DIRECT"
                })
            except Exception as e:
                logger.warning(f"Failed to parse flight: {e}")
                continue
        
        return parsed_flights


def get_aviationstack_mcp_client() -> AviationStackMCPClient:
    """Get singleton instance of AviationStack MCP client."""
    return AviationStackMCPClient()
