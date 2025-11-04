"""
Google Maps MCP Client (Optional)

Provides Google Maps integration when API key is available.
This is optional and gracefully handles missing API keys.
"""

import os
import logging
from typing import Dict, List, Optional
from backend.services.location_service import LocationService

logger = logging.getLogger(__name__)


class GoogleMapsMCPError(Exception):
    """Exception raised for Google Maps MCP client errors."""
    pass


class GoogleMapsMCPClient:
    """
    Client for Google Maps MCP Server (Optional).
    
    Only works if GOOGLE_MAPS_API_KEY environment variable is set.
    Falls back gracefully if not available.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Google Maps MCP client.
        
        Args:
            api_key: Google Maps API key (optional)
        """
        self.api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
        self.enabled = bool(self.api_key)
        
        if self.enabled:
            # Import location service which uses Google Maps
            try:
                from services.location_service import LocationService
                self.location_service = LocationService
                logger.info("Google Maps MCP client enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Google Maps: {e}")
                self.enabled = False
        else:
            logger.info("Google Maps MCP client disabled (no API key)")
    
    def is_enabled(self) -> bool:
        """Check if Google Maps integration is enabled."""
        return self.enabled
    
    def get_airport_location(
        self,
        airport_code: str,
        db_session = None,
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Get airport location with timezone (if enabled).
        
        Args:
            airport_code: IATA airport code
            db_session: Database session
            force_refresh: Force refresh from API
        
        Returns:
            Dict with airport location or None if disabled
        """
        if not self.enabled:
            return None
        
        if not db_session:
            logger.warning("No database session provided for Google Maps")
            return None
        
        try:
            service = self.location_service(db_session)
            return service.get_airport_location(airport_code, force_refresh)
        except Exception as e:
            logger.error(f"Google Maps lookup failed: {e}")
            return None
    
    def get_route_distance(
        self,
        origin: str,
        destination: str,
        db_session = None,
        force_refresh: bool = False
    ) -> Optional[Dict]:
        """
        Get distance between airports (if enabled).
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            db_session: Database session
            force_refresh: Force refresh from API
        
        Returns:
            Dict with distance data or None if disabled
        """
        if not self.enabled:
            return None
        
        if not db_session:
            logger.warning("No database session provided for Google Maps")
            return None
        
        try:
            service = self.location_service(db_session)
            return service.get_route_distance(origin, destination, force_refresh)
        except Exception as e:
            logger.error(f"Google Maps distance failed: {e}")
            return None
    
    def geocode_address(
        self,
        address: str,
        db_session = None
    ) -> Optional[Dict]:
        """
        Geocode an address (if enabled).
        
        Args:
            address: Address string
            db_session: Database session
        
        Returns:
            Dict with coordinates or None if disabled
        """
        if not self.enabled:
            return None
        
        if not db_session:
            logger.warning("No database session provided for Google Maps")
            return None
        
        try:
            service = self.location_service(db_session)
            return service.geocode_and_cache(address)
        except Exception as e:
            logger.error(f"Google Maps geocoding failed: {e}")
            return None


def get_googlemaps_mcp_client() -> GoogleMapsMCPClient:
    """Get singleton instance of Google Maps MCP client."""
    return GoogleMapsMCPClient()
