"""
AviationStack API Client for PreFlight AI
Real-time and historical flight data integration
"""
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


class AviationStackError(Exception):
    """Custom exception for AviationStack API errors"""
    pass


class AviationStackClient:
    """
    Client for AviationStack API
    Provides real-time and historical flight data
    """

    BASE_URL = "https://api.aviationstack.com/v1"

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("AVIATIONSTACK_API_KEY", "00a88306b41eda9c29cc2b29732c51e6")
        if not self.api_key:
            raise ValueError("AviationStack API key not provided")

        # Configure session with retries
        self.session = requests.Session()
        retries = Retry(
            total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))

    def get_real_time_flights(
        self,
        flight_iata: Optional[str] = None,
        flight_number: Optional[str] = None,
        airline_name: Optional[str] = None,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get real-time flight data.

        Args:
            flight_iata: IATA flight code (e.g., 'EK230')
            flight_number: Flight number
            airline_name: Airline name or IATA code
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            limit: Maximum number of results

        Returns:
            list: List of flight data dictionaries
        """
        params = {"access_key": self.api_key, "limit": limit}

        if flight_iata:
            params["flight_iata"] = flight_iata
        if flight_number:
            params["flight_number"] = flight_number
        if airline_name:
            params["airline_name"] = airline_name
        if dep_iata:
            params["dep_iata"] = dep_iata
        if arr_iata:
            params["arr_iata"] = arr_iata

        try:
            response = self.session.get(
                f"{self.BASE_URL}/flights", params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise AviationStackError(f"API Error: {data['error']}")

            return self._parse_flight_data(data.get("data", []))

        except requests.exceptions.RequestException as e:
            raise AviationStackError(f"AviationStack API request failed: {str(e)}")

    def get_historical_flights(
        self,
        flight_date: str,
        flight_iata: Optional[str] = None,
        dep_iata: Optional[str] = None,
        arr_iata: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """
        Get historical flight data for a specific date.

        Args:
            flight_date: Date in format 'YYYY-MM-DD'
            flight_iata: IATA flight code
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            limit: Maximum number of results

        Returns:
            list: List of historical flight data
        """
        params = {
            "access_key": self.api_key,
            "flight_date": flight_date,
            "limit": limit,
        }

        if flight_iata:
            params["flight_iata"] = flight_iata
        if dep_iata:
            params["dep_iata"] = dep_iata
        if arr_iata:
            params["arr_iata"] = arr_iata

        try:
            response = self.session.get(
                f"{self.BASE_URL}/flights", params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise AviationStackError(f"API Error: {data['error']}")

            return self._parse_flight_data(data.get("data", []))

        except requests.exceptions.RequestException as e:
            raise AviationStackError(f"Historical flight request failed: {str(e)}")

    def get_flight_route_history(
        self, dep_iata: str, arr_iata: str, days_back: int = 30
    ) -> List[Dict]:
        """
        Get historical data for a specific route over multiple days.

        Args:
            dep_iata: Departure airport IATA code
            arr_iata: Arrival airport IATA code
            days_back: Number of days to look back

        Returns:
            list: Aggregated historical flight data for the route
        """
        all_flights = []
        today = datetime.now()

        for i in range(days_back):
            date = (today - timedelta(days=i)).strftime("%Y-%m-%d")
            try:
                flights = self.get_historical_flights(
                    flight_date=date, dep_iata=dep_iata, arr_iata=arr_iata, limit=100
                )
                all_flights.extend(flights)
            except AviationStackError as e:
                print(f"Warning: Failed to get data for {date}: {e}")
                continue

        return all_flights

    def get_airline_routes(
        self, airline_iata: Optional[str] = None, limit: int = 100
    ) -> List[Dict]:
        """
        Get airline routes.

        Args:
            airline_iata: Airline IATA code (e.g., 'EK' for Emirates)
            limit: Maximum number of results

        Returns:
            list: List of route data
        """
        params = {"access_key": self.api_key, "limit": limit}

        if airline_iata:
            params["airline_iata"] = airline_iata

        try:
            response = self.session.get(
                f"{self.BASE_URL}/routes", params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise AviationStackError(f"API Error: {data['error']}")

            return data.get("data", [])

        except requests.exceptions.RequestException as e:
            raise AviationStackError(f"Routes request failed: {str(e)}")

    def get_airport_info(self, airport_iata: str) -> Dict:
        """
        Get detailed airport information.

        Args:
            airport_iata: Airport IATA code

        Returns:
            dict: Airport information
        """
        params = {"access_key": self.api_key, "iata_code": airport_iata}

        try:
            response = self.session.get(
                f"{self.BASE_URL}/airports", params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise AviationStackError(f"API Error: {data['error']}")

            airports = data.get("data", [])
            return airports[0] if airports else {}

        except requests.exceptions.RequestException as e:
            raise AviationStackError(f"Airport info request failed: {str(e)}")

    def get_airline_info(self, airline_iata: str) -> Dict:
        """
        Get detailed airline information.

        Args:
            airline_iata: Airline IATA code

        Returns:
            dict: Airline information
        """
        params = {"access_key": self.api_key, "iata_code": airline_iata}

        try:
            response = self.session.get(
                f"{self.BASE_URL}/airlines", params=params, timeout=15
            )
            response.raise_for_status()
            data = response.json()

            if "error" in data:
                raise AviationStackError(f"API Error: {data['error']}")

            airlines = data.get("data", [])
            return airlines[0] if airlines else {}

        except requests.exceptions.RequestException as e:
            raise AviationStackError(f"Airline info request failed: {str(e)}")

    def _parse_flight_data(self, flights: List[Dict]) -> List[Dict]:
        """
        Parse and standardize flight data from AviationStack.

        Args:
            flights: Raw flight data from API

        Returns:
            list: Standardized flight data
        """
        parsed_flights = []

        for flight in flights:
            try:
                # Extract departure and arrival info
                departure = flight.get("departure", {})
                arrival = flight.get("arrival", {})
                flight_info = flight.get("flight", {})
                airline = flight.get("airline", {})

                # Calculate delay if actual times are available
                scheduled_dep = departure.get("scheduled")
                actual_dep = departure.get("actual")
                delay_minutes = None

                if scheduled_dep and actual_dep:
                    scheduled_dt = datetime.fromisoformat(scheduled_dep.replace("Z", "+00:00"))
                    actual_dt = datetime.fromisoformat(actual_dep.replace("Z", "+00:00"))
                    delay_minutes = int((actual_dt - scheduled_dt).total_seconds() / 60)

                parsed_flight = {
                    # Flight identifiers
                    "flight_iata": flight_info.get("iata"),
                    "flight_icao": flight_info.get("icao"),
                    "flight_number": flight_info.get("number"),
                    # Airline info
                    "airline_name": airline.get("name"),
                    "airline_iata": airline.get("iata"),
                    "airline_icao": airline.get("icao"),
                    # Departure
                    "dep_airport": departure.get("airport"),
                    "dep_iata": departure.get("iata"),
                    "dep_icao": departure.get("icao"),
                    "dep_scheduled": scheduled_dep,
                    "dep_actual": actual_dep,
                    "dep_estimated": departure.get("estimated"),
                    "dep_delay": departure.get("delay"),
                    "dep_terminal": departure.get("terminal"),
                    "dep_gate": departure.get("gate"),
                    # Arrival
                    "arr_airport": arrival.get("airport"),
                    "arr_iata": arrival.get("iata"),
                    "arr_icao": arrival.get("icao"),
                    "arr_scheduled": arrival.get("scheduled"),
                    "arr_actual": arrival.get("actual"),
                    "arr_estimated": arrival.get("estimated"),
                    "arr_delay": arrival.get("delay"),
                    "arr_terminal": arrival.get("terminal"),
                    "arr_gate": arrival.get("gate"),
                    # Status
                    "flight_status": flight.get("flight_status"),
                    "flight_date": flight.get("flight_date"),
                    # Calculated delay
                    "delay_minutes": delay_minutes,
                    "is_delayed": delay_minutes > 15 if delay_minutes is not None else None,
                }

                parsed_flights.append(parsed_flight)

            except Exception as e:
                print(f"Warning: Failed to parse flight data: {e}")
                continue

        return parsed_flights

    def calculate_route_statistics(self, route_history: List[Dict]) -> Dict:
        """
        Calculate delay statistics for a route based on historical data.

        Args:
            route_history: List of historical flights for a route

        Returns:
            dict: Route statistics including average delay, on-time percentage, etc.
        """
        if not route_history:
            return {
                "total_flights": 0,
                "avg_delay_minutes": 0,
                "on_time_percentage": 0,
                "delayed_flights": 0,
            }

        delays = [f["delay_minutes"] for f in route_history if f.get("delay_minutes") is not None]
        
        if not delays:
            return {
                "total_flights": len(route_history),
                "avg_delay_minutes": 0,
                "on_time_percentage": 0,
                "delayed_flights": 0,
            }

        delayed_count = sum(1 for d in delays if d > 15)
        on_time_count = len(delays) - delayed_count

        return {
            "total_flights": len(route_history),
            "flights_with_data": len(delays),
            "avg_delay_minutes": round(sum(delays) / len(delays), 2),
            "max_delay_minutes": max(delays),
            "min_delay_minutes": min(delays),
            "on_time_flights": on_time_count,
            "delayed_flights": delayed_count,
            "on_time_percentage": round((on_time_count / len(delays)) * 100, 2),
            "delay_percentage": round((delayed_count / len(delays)) * 100, 2),
        }


def get_aviationstack_client() -> AviationStackClient:
    """Get singleton AviationStack client instance."""
    return AviationStackClient()


__all__ = ["AviationStackError", "AviationStackClient", "get_aviationstack_client"]
