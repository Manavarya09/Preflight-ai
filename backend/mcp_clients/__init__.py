"""
MCP Clients Package

Provides unified access to Model Context Protocol (MCP) servers:
- OpenMeteo MCP Server (weather data)
- AviationStack MCP Server (flight tracking)
- Google Maps MCP Client (geocoding - optional)
"""

from .openmeteo_mcp_client import OpenMeteoMCPClient, OpenMeteoMCPError
from .aviationstack_mcp_client import AviationStackMCPClient, AviationStackMCPError
from .googlemaps_mcp_client import GoogleMapsMCPClient, GoogleMapsMCPError

__all__ = [
    'OpenMeteoMCPClient',
    'OpenMeteoMCPError',
    'AviationStackMCPClient',
    'AviationStackMCPError',
    'GoogleMapsMCPClient',
    'GoogleMapsMCPError',
]
