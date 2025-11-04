"""
Location Service - Integrates Google Maps with database caching
Provides worldwide airport analysis and location services
"""
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database.models import AirportLocation, RouteDistance, GeocodingCache
from external_apis.google_maps_service import GoogleMapsService, GoogleMapsError


class LocationService:
    """
    High-level location service with intelligent caching
    Minimizes Google Maps API calls through database caching
    """
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self.maps_service = GoogleMapsService()
        self.cache_ttl_days = 90  # Cache airport locations for 90 days
        self.geocoding_cache_days = 30  # Cache general geocoding for 30 days
    
    def get_airport_location(
        self,
        airport_code: str,
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Get airport location with intelligent caching
        
        Args:
            airport_code: IATA airport code
            force_refresh: Force refresh from Google Maps API
        
        Returns:
            dict: Airport location data
        """
        airport_code = airport_code.upper().strip()
        
        # Check database cache first
        if not force_refresh:
            cached = self.db.query(AirportLocation).filter(
                AirportLocation.airport_code == airport_code
            ).first()
            
            if cached:
                # Check if cache is still valid
                days_old = (datetime.now() - cached.last_verified).days
                if days_old < self.cache_ttl_days:
                    # Update access count
                    return self._airport_location_to_dict(cached)
        
        # Fetch from Google Maps
        try:
            search_query = f"{airport_code} airport"
            location_data = self.maps_service.geocode_address(search_query)
            
            if not location_data:
                return None
            
            # Get timezone information
            timezone_data = self.maps_service.get_timezone(
                location_data["latitude"],
                location_data["longitude"]
            )
            
            # Extract city and country from address components
            city, country = self._extract_city_country(
                location_data.get("address_components", [])
            )
            
            # Upsert to database
            airport_loc = self.db.query(AirportLocation).filter(
                AirportLocation.airport_code == airport_code
            ).first()
            
            if airport_loc:
                # Update existing
                airport_loc.latitude = location_data["latitude"]
                airport_loc.longitude = location_data["longitude"]
                airport_loc.formatted_address = location_data["formatted_address"]
                airport_loc.google_place_id = location_data.get("place_id")
                airport_loc.city = city
                airport_loc.country = country
                airport_loc.timezone_id = timezone_data.get("timezone_id") if timezone_data else None
                airport_loc.timezone_name = timezone_data.get("timezone_name") if timezone_data else None
                airport_loc.utc_offset_seconds = (
                    timezone_data.get("raw_offset", 0) + timezone_data.get("dst_offset", 0)
                    if timezone_data else None
                )
                airport_loc.last_verified = datetime.now()
                airport_loc.updated_at = datetime.now()
            else:
                # Create new
                airport_loc = AirportLocation(
                    airport_code=airport_code,
                    airport_name=f"{airport_code} Airport",  # Simplified
                    latitude=location_data["latitude"],
                    longitude=location_data["longitude"],
                    formatted_address=location_data["formatted_address"],
                    google_place_id=location_data.get("place_id"),
                    city=city,
                    country=country,
                    timezone_id=timezone_data.get("timezone_id") if timezone_data else None,
                    timezone_name=timezone_data.get("timezone_name") if timezone_data else None,
                    utc_offset_seconds=(
                        timezone_data.get("raw_offset", 0) + timezone_data.get("dst_offset", 0)
                        if timezone_data else None
                    ),
                    source="GOOGLE_MAPS"
                )
                self.db.add(airport_loc)
            
            self.db.commit()
            self.db.refresh(airport_loc)
            
            return self._airport_location_to_dict(airport_loc)
            
        except GoogleMapsError as e:
            # If API fails, return cached data even if expired
            cached = self.db.query(AirportLocation).filter(
                AirportLocation.airport_code == airport_code
            ).first()
            if cached:
                return self._airport_location_to_dict(cached)
            raise
    
    def get_route_distance(
        self,
        origin: str,
        destination: str,
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Get distance between two airports with caching
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            force_refresh: Force refresh from Google Maps API
        
        Returns:
            dict: Route distance data
        """
        origin = origin.upper().strip()
        destination = destination.upper().strip()
        
        if origin == destination:
            raise ValueError("Origin and destination must be different")
        
        # Check database cache
        if not force_refresh:
            cached = self.db.query(RouteDistance).filter(
                RouteDistance.origin_airport == origin,
                RouteDistance.destination_airport == destination
            ).first()
            
            if cached:
                days_old = (datetime.now() - cached.last_calculated).days
                if days_old < self.cache_ttl_days:
                    return self._route_distance_to_dict(cached)
        
        # Get airport locations
        origin_loc = self.get_airport_location(origin)
        dest_loc = self.get_airport_location(destination)
        
        if not origin_loc or not dest_loc:
            return None
        
        # Calculate great circle distance
        great_circle_km = self._haversine_distance(
            origin_loc["latitude"],
            origin_loc["longitude"],
            dest_loc["latitude"],
            dest_loc["longitude"]
        )
        
        # Get more accurate distance from Google Maps Distance Matrix
        try:
            origin_coords = f"{origin_loc['latitude']},{origin_loc['longitude']}"
            dest_coords = f"{dest_loc['latitude']},{dest_loc['longitude']}"
            
            distance_matrix = self.maps_service.calculate_distance_matrix(
                origins=[origin_coords],
                destinations=[dest_coords],
                mode="driving"  # Best approximation for ground distance
            )
            
            if distance_matrix and distance_matrix.get("rows"):
                element = distance_matrix["rows"][0][0]
                if element.get("status") == "OK":
                    distance_meters = element["distance_meters"]
                else:
                    # Fallback to great circle if no route found
                    distance_meters = int(great_circle_km * 1000)
            else:
                distance_meters = int(great_circle_km * 1000)
                
        except GoogleMapsError:
            # Fallback to great circle distance
            distance_meters = int(great_circle_km * 1000)
        
        # Estimate flight duration (rough estimate: 800 km/h average)
        estimated_duration_minutes = int((great_circle_km / 800) * 60)
        
        # Upsert to database
        route_dist = self.db.query(RouteDistance).filter(
            RouteDistance.origin_airport == origin,
            RouteDistance.destination_airport == destination
        ).first()
        
        if route_dist:
            route_dist.distance_meters = distance_meters
            route_dist.great_circle_distance_km = great_circle_km
            route_dist.average_flight_duration_minutes = estimated_duration_minutes
            route_dist.last_calculated = datetime.now()
            route_dist.updated_at = datetime.now()
        else:
            route_dist = RouteDistance(
                origin_airport=origin,
                destination_airport=destination,
                distance_meters=distance_meters,
                great_circle_distance_km=great_circle_km,
                average_flight_duration_minutes=estimated_duration_minutes,
                source="GOOGLE_MAPS"
            )
            self.db.add(route_dist)
        
        try:
            self.db.commit()
            self.db.refresh(route_dist)
        except IntegrityError:
            self.db.rollback()
            # Race condition - fetch again
            route_dist = self.db.query(RouteDistance).filter(
                RouteDistance.origin_airport == origin,
                RouteDistance.destination_airport == destination
            ).first()
        
        return self._route_distance_to_dict(route_dist)
    
    def geocode_and_cache(self, address: str) -> Optional[Dict]:
        """
        Geocode address with intelligent caching
        
        Args:
            address: Address string to geocode
        
        Returns:
            dict: Geocoded location data
        """
        # Generate hash for cache key
        query_hash = hashlib.sha256(address.lower().strip().encode()).hexdigest()
        
        # Check cache
        cached = self.db.query(GeocodingCache).filter(
            GeocodingCache.search_query_hash == query_hash,
            GeocodingCache.expires_at > datetime.now()
        ).first()
        
        if cached:
            # Update hit count
            cached.cache_hits += 1
            self.db.commit()
            return {
                "latitude": float(cached.latitude),
                "longitude": float(cached.longitude),
                "formatted_address": cached.formatted_address,
                "place_id": cached.google_place_id,
                "from_cache": True
            }
        
        # Geocode with Google Maps
        try:
            location_data = self.maps_service.geocode_address(address)
            
            if not location_data:
                return None
            
            # Store in cache
            expires_at = datetime.now() + timedelta(days=self.geocoding_cache_days)
            
            cache_entry = GeocodingCache(
                search_query=address[:1000],  # Limit query length
                search_query_hash=query_hash,
                latitude=location_data["latitude"],
                longitude=location_data["longitude"],
                formatted_address=location_data["formatted_address"],
                google_place_id=location_data.get("place_id"),
                location_type=location_data.get("location_type"),
                address_components=location_data.get("address_components"),
                viewport=location_data.get("viewport"),
                expires_at=expires_at
            )
            
            self.db.add(cache_entry)
            self.db.commit()
            
            return {
                "latitude": location_data["latitude"],
                "longitude": location_data["longitude"],
                "formatted_address": location_data["formatted_address"],
                "place_id": location_data.get("place_id"),
                "from_cache": False
            }
            
        except GoogleMapsError:
            raise
    
    def get_nearby_airports(
        self,
        latitude: float,
        longitude: float,
        radius_km: float = 100
    ) -> List[Dict]:
        """
        Find airports within radius of coordinates
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            radius_km: Search radius in kilometers
        
        Returns:
            list: Nearby airports with distances
        """
        # Query all airports (in production, use spatial index)
        all_airports = self.db.query(AirportLocation).all()
        
        nearby = []
        for airport in all_airports:
            distance = self._haversine_distance(
                latitude,
                longitude,
                float(airport.latitude),
                float(airport.longitude)
            )
            
            if distance <= radius_km:
                airport_dict = self._airport_location_to_dict(airport)
                airport_dict["distance_km"] = round(distance, 2)
                nearby.append(airport_dict)
        
        # Sort by distance
        nearby.sort(key=lambda x: x["distance_km"])
        
        return nearby
    
    def validate_airport_coordinates(
        self,
        airport_code: str,
        latitude: float,
        longitude: float,
        tolerance_km: float = 50.0
    ) -> bool:
        """
        Validate if provided coordinates match expected airport location
        
        Args:
            airport_code: IATA airport code
            latitude: Latitude to validate
            longitude: Longitude to validate
            tolerance_km: Tolerance in kilometers
        
        Returns:
            bool: True if coordinates are within tolerance
        """
        airport_loc = self.get_airport_location(airport_code)
        
        if not airport_loc:
            return False
        
        distance = self._haversine_distance(
            latitude,
            longitude,
            airport_loc["latitude"],
            airport_loc["longitude"]
        )
        
        return distance <= tolerance_km
    
    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """
        Calculate great circle distance between two points
        
        Returns:
            float: Distance in kilometers
        """
        from math import radians, cos, sin, asin, sqrt
        
        lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
        
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Earth radius in kilometers
        
        return c * r
    
    def _extract_city_country(self, address_components: List[Dict]) -> Tuple[Optional[str], Optional[str]]:
        """Extract city and country from Google Maps address components"""
        city = None
        country = None
        
        for component in address_components:
            types = component.get("types", [])
            
            if "locality" in types:
                city = component.get("long_name")
            elif "administrative_area_level_1" in types and not city:
                city = component.get("long_name")
            
            if "country" in types:
                country = component.get("long_name")
        
        return city, country
    
    def _airport_location_to_dict(self, airport: AirportLocation) -> Dict:
        """Convert AirportLocation ORM to dict"""
        return {
            "airport_code": airport.airport_code,
            "airport_name": airport.airport_name,
            "city": airport.city,
            "country": airport.country,
            "latitude": float(airport.latitude),
            "longitude": float(airport.longitude),
            "formatted_address": airport.formatted_address,
            "place_id": airport.google_place_id,
            "timezone_id": airport.timezone_id,
            "timezone_name": airport.timezone_name,
            "utc_offset_seconds": airport.utc_offset_seconds,
            "elevation_meters": airport.elevation_meters,
            "last_verified": airport.last_verified.isoformat() if airport.last_verified else None
        }
    
    def _route_distance_to_dict(self, route: RouteDistance) -> Dict:
        """Convert RouteDistance ORM to dict"""
        return {
            "origin": route.origin_airport,
            "destination": route.destination_airport,
            "distance_meters": route.distance_meters,
            "distance_km": float(route.distance_meters / 1000),
            "distance_nm": float(route.distance_meters / 1852),
            "great_circle_km": float(route.great_circle_distance_km) if route.great_circle_distance_km else None,
            "estimated_flight_duration_minutes": route.average_flight_duration_minutes,
            "last_calculated": route.last_calculated.isoformat() if route.last_calculated else None
        }


__all__ = ["LocationService"]
