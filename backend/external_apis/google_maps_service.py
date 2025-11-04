"""
Google Maps Platform Integration for PreFlight AI
Provides geocoding, distance matrix, and location services for worldwide airport analysis
"""
import os
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from urllib.parse import urlencode

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class GoogleMapsError(Exception):
    """Custom exception for Google Maps API errors"""
    pass


class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, max_calls: int, time_window: int = 60):
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_make_call(self) -> bool:
        """Check if we can make another API call"""
        now = time.time()
        self.calls = [call_time for call_time in self.calls 
                      if now - call_time < self.time_window]
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record an API call"""
        self.calls.append(time.time())


class GoogleMapsService:
    """
    Production-grade Google Maps Platform client
    Implements geocoding, distance matrix, and places services
    """
    
    GEOCODING_BASE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
    DISTANCE_MATRIX_BASE_URL = "https://maps.googleapis.com/maps/api/distancematrix/json"
    PLACES_BASE_URL = "https://maps.googleapis.com/maps/api/place/findplacefromtext/json"
    TIMEZONE_BASE_URL = "https://maps.googleapis.com/maps/api/timezone/json"
    
    def __init__(self):
        # SECURITY: API key loaded from environment, never hardcoded
        self.api_key = os.getenv("GOOGLE_MAPS_API_KEY")
        if not self.api_key or self.api_key == "your_google_maps_api_key_here":
            raise GoogleMapsError(
                "GOOGLE_MAPS_API_KEY not configured. "
                "Set environment variable with your API key."
            )
        
        # Rate limiting to prevent quota exhaustion
        rate_limit = int(os.getenv("GOOGLE_MAPS_RATE_LIMIT_PER_MINUTE", "50"))
        self.rate_limiter = RateLimiter(max_calls=rate_limit, time_window=60)
        
        # Session with retry logic
        self.session = requests.Session()
        retries = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST"]
        )
        self.session.mount("https://", HTTPAdapter(max_retries=retries))
        
        # In-memory cache for geocoding results (production: use Redis)
        self.geocode_cache = {}
        self.cache_ttl = int(os.getenv("GOOGLE_MAPS_CACHE_TTL_SECONDS", "86400"))
    
    def _check_rate_limit(self):
        """Enforce rate limiting"""
        if not self.rate_limiter.can_make_call():
            raise GoogleMapsError(
                "Rate limit exceeded. Please wait before making more requests."
            )
        self.rate_limiter.record_call()
    
    def _get_cache_key(self, prefix: str, *args) -> str:
        """Generate cache key from arguments"""
        key_str = f"{prefix}:" + ":".join(str(arg) for arg in args)
        return hashlib.md5(key_str.encode()).hexdigest()
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cached entry is still valid"""
        if "timestamp" not in cache_entry:
            return False
        cached_time = cache_entry["timestamp"]
        return (datetime.now() - cached_time).total_seconds() < self.cache_ttl
    
    def geocode_address(self, address: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Convert address to geographic coordinates
        
        Args:
            address: Address string (e.g., "Dubai International Airport")
            use_cache: Whether to use cached results
        
        Returns:
            dict: Location data with lat, lng, formatted_address, place_id
        """
        # Input validation
        if not address or not isinstance(address, str):
            raise GoogleMapsError("Invalid address provided")
        
        address = address.strip()
        if len(address) < 3:
            raise GoogleMapsError("Address too short")
        
        # Check cache
        cache_key = self._get_cache_key("geocode", address.lower())
        if use_cache and cache_key in self.geocode_cache:
            cached = self.geocode_cache[cache_key]
            if self._is_cache_valid(cached):
                return cached["data"]
        
        # Rate limiting
        self._check_rate_limit()
        
        try:
            params = {
                "address": address,
                "key": self.api_key
            }
            
            response = self.session.get(
                self.GEOCODING_BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("error_message", data.get("status"))
                raise GoogleMapsError(f"Geocoding failed: {error_msg}")
            
            if not data.get("results"):
                return None
            
            result = data["results"][0]
            location_data = {
                "latitude": result["geometry"]["location"]["lat"],
                "longitude": result["geometry"]["location"]["lng"],
                "formatted_address": result["formatted_address"],
                "place_id": result.get("place_id"),
                "address_components": result.get("address_components", []),
                "location_type": result["geometry"].get("location_type"),
                "viewport": result["geometry"].get("viewport")
            }
            
            # Cache result
            self.geocode_cache[cache_key] = {
                "data": location_data,
                "timestamp": datetime.now()
            }
            
            return location_data
            
        except requests.exceptions.RequestException as e:
            raise GoogleMapsError(f"Geocoding request failed: {str(e)}")
    
    def reverse_geocode(
        self, 
        latitude: float, 
        longitude: float,
        use_cache: bool = True
    ) -> Optional[Dict]:
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            use_cache: Whether to use cached results
        
        Returns:
            dict: Address data with formatted_address and components
        """
        # Input validation
        if not (-90 <= latitude <= 90):
            raise GoogleMapsError("Invalid latitude: must be between -90 and 90")
        if not (-180 <= longitude <= 180):
            raise GoogleMapsError("Invalid longitude: must be between -180 and 180")
        
        # Check cache
        cache_key = self._get_cache_key("reverse", latitude, longitude)
        if use_cache and cache_key in self.geocode_cache:
            cached = self.geocode_cache[cache_key]
            if self._is_cache_valid(cached):
                return cached["data"]
        
        # Rate limiting
        self._check_rate_limit()
        
        try:
            params = {
                "latlng": f"{latitude},{longitude}",
                "key": self.api_key
            }
            
            response = self.session.get(
                self.GEOCODING_BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("error_message", data.get("status"))
                raise GoogleMapsError(f"Reverse geocoding failed: {error_msg}")
            
            if not data.get("results"):
                return None
            
            result = data["results"][0]
            address_data = {
                "formatted_address": result["formatted_address"],
                "address_components": result.get("address_components", []),
                "place_id": result.get("place_id"),
                "location_type": result["geometry"].get("location_type")
            }
            
            # Cache result
            self.geocode_cache[cache_key] = {
                "data": address_data,
                "timestamp": datetime.now()
            }
            
            return address_data
            
        except requests.exceptions.RequestException as e:
            raise GoogleMapsError(f"Reverse geocoding request failed: {str(e)}")
    
    def calculate_distance_matrix(
        self,
        origins: List[str],
        destinations: List[str],
        mode: str = "driving",
        units: str = "metric"
    ) -> Dict:
        """
        Calculate travel distance and time between multiple points
        
        Args:
            origins: List of origin addresses or coordinates
            destinations: List of destination addresses or coordinates
            mode: Travel mode (driving, walking, bicycling, transit)
            units: Unit system (metric, imperial)
        
        Returns:
            dict: Distance matrix with distances and durations
        """
        # Input validation
        if not origins or not destinations:
            raise GoogleMapsError("Origins and destinations cannot be empty")
        
        if len(origins) > 25 or len(destinations) > 25:
            raise GoogleMapsError("Maximum 25 origins/destinations per request")
        
        valid_modes = ["driving", "walking", "bicycling", "transit"]
        if mode not in valid_modes:
            raise GoogleMapsError(f"Invalid mode. Must be one of: {valid_modes}")
        
        # Rate limiting
        self._check_rate_limit()
        
        try:
            params = {
                "origins": "|".join(origins),
                "destinations": "|".join(destinations),
                "mode": mode,
                "units": units,
                "key": self.api_key
            }
            
            response = self.session.get(
                self.DISTANCE_MATRIX_BASE_URL,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("error_message", data.get("status"))
                raise GoogleMapsError(f"Distance matrix failed: {error_msg}")
            
            # Parse results
            result = {
                "origin_addresses": data.get("origin_addresses", []),
                "destination_addresses": data.get("destination_addresses", []),
                "rows": []
            }
            
            for row in data.get("rows", []):
                elements = []
                for element in row.get("elements", []):
                    if element.get("status") == "OK":
                        elements.append({
                            "distance_meters": element["distance"]["value"],
                            "distance_text": element["distance"]["text"],
                            "duration_seconds": element["duration"]["value"],
                            "duration_text": element["duration"]["text"],
                            "status": "OK"
                        })
                    else:
                        elements.append({
                            "status": element.get("status"),
                            "error": "Route not found"
                        })
                result["rows"].append(elements)
            
            return result
            
        except requests.exceptions.RequestException as e:
            raise GoogleMapsError(f"Distance matrix request failed: {str(e)}")
    
    def find_airport_by_name(self, airport_name: str) -> Optional[Dict]:
        """
        Find airport details by name using Places API
        
        Args:
            airport_name: Airport name to search
        
        Returns:
            dict: Airport details with coordinates and place_id
        """
        # Input validation
        if not airport_name or not isinstance(airport_name, str):
            raise GoogleMapsError("Invalid airport name provided")
        
        # Rate limiting
        self._check_rate_limit()
        
        try:
            params = {
                "input": airport_name,
                "inputtype": "textquery",
                "fields": "place_id,name,geometry,formatted_address,types",
                "key": self.api_key
            }
            
            response = self.session.get(
                self.PLACES_BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                return None
            
            if not data.get("candidates"):
                return None
            
            place = data["candidates"][0]
            
            # Filter for airports only
            if "airport" not in place.get("types", []):
                return None
            
            return {
                "place_id": place["place_id"],
                "name": place["name"],
                "latitude": place["geometry"]["location"]["lat"],
                "longitude": place["geometry"]["location"]["lng"],
                "formatted_address": place.get("formatted_address"),
                "types": place.get("types", [])
            }
            
        except requests.exceptions.RequestException as e:
            raise GoogleMapsError(f"Places search failed: {str(e)}")
    
    def get_timezone(self, latitude: float, longitude: float) -> Optional[Dict]:
        """
        Get timezone information for coordinates
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            dict: Timezone data with timezone_id, name, and UTC offset
        """
        # Input validation
        if not (-90 <= latitude <= 90):
            raise GoogleMapsError("Invalid latitude")
        if not (-180 <= longitude <= 180):
            raise GoogleMapsError("Invalid longitude")
        
        # Rate limiting
        self._check_rate_limit()
        
        try:
            timestamp = int(time.time())
            params = {
                "location": f"{latitude},{longitude}",
                "timestamp": timestamp,
                "key": self.api_key
            }
            
            response = self.session.get(
                self.TIMEZONE_BASE_URL,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "OK":
                error_msg = data.get("error_message", data.get("status"))
                raise GoogleMapsError(f"Timezone lookup failed: {error_msg}")
            
            return {
                "timezone_id": data["timeZoneId"],
                "timezone_name": data["timeZoneName"],
                "raw_offset": data["rawOffset"],
                "dst_offset": data["dstOffset"]
            }
            
        except requests.exceptions.RequestException as e:
            raise GoogleMapsError(f"Timezone request failed: {str(e)}")
    
    def validate_airport_location(
        self,
        airport_code: str,
        expected_lat: float,
        expected_lng: float,
        tolerance_km: float = 50.0
    ) -> bool:
        """
        Validate if coordinates match expected airport location
        
        Args:
            airport_code: IATA airport code
            expected_lat: Expected latitude
            expected_lng: Expected longitude
            tolerance_km: Tolerance in kilometers
        
        Returns:
            bool: True if location is within tolerance
        """
        try:
            # Geocode airport
            location = self.geocode_address(f"{airport_code} airport")
            if not location:
                return False
            
            # Calculate distance using Haversine formula
            from math import radians, cos, sin, asin, sqrt
            
            lat1, lon1 = radians(expected_lat), radians(expected_lng)
            lat2, lon2 = radians(location["latitude"]), radians(location["longitude"])
            
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            r = 6371  # Earth radius in kilometers
            
            distance = c * r
            
            return distance <= tolerance_km
            
        except Exception:
            return False
    
    def clear_cache(self):
        """Clear all cached geocoding results"""
        self.geocode_cache.clear()


def get_google_maps_service() -> GoogleMapsService:
    """Get singleton Google Maps service instance"""
    return GoogleMapsService()


__all__ = [
    "GoogleMapsError",
    "GoogleMapsService",
    "get_google_maps_service",
    "RateLimiter"
]
