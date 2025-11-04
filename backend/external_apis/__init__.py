"""
External API clients for PreFlight AI
"""
from external_apis.weather import (
    WeatherAPIError,
    WeatherService,
    get_weather_service,
)
from external_apis.notifications import (
    NotificationError,
    NotificationService,
    get_notification_service,
)
from external_apis.flight_tracking import (
    AviationStackClient,
    AviationStackError,
)
from external_apis.openmeteo_weather import (
    OpenMeteoClient,
    OpenMeteoError,
    AIRPORT_COORDINATES,
    get_openmeteo_client,
)
from external_apis.google_maps_service import (
    GoogleMapsService,
    GoogleMapsError,
    get_google_maps_service,
    RateLimiter,
)

__all__ = [
    # Weather
    "WeatherAPIError",
    "WeatherService",
    "get_weather_service",
    "OpenMeteoClient",
    "OpenMeteoError",
    "AIRPORT_COORDINATES",
    "get_openmeteo_client",
    # Notifications
    "NotificationError",
    "NotificationService",
    "get_notification_service",
    # Flight Tracking
    "AviationStackClient",
    "AviationStackError",
    # Google Maps
    "GoogleMapsService",
    "GoogleMapsError",
    "get_google_maps_service",
    "RateLimiter",
]
