"""
MCP Configuration Module

Centralized configuration for all MCP servers.
Provides environment-based configuration with sensible defaults.
"""

import os
from typing import Dict


class MCPConfig:
    """Configuration for all MCP servers."""
    
    # OpenMeteo MCP Server
    OPENMETEO_MCP_SERVER_URL = os.getenv(
        "OPENMETEO_MCP_SERVER_URL", 
        "http://localhost:3000"
    )
    
    # AviationStack MCP Server
    AVIATIONSTACK_MCP_SERVER_URL = os.getenv(
        "AVIATIONSTACK_MCP_SERVER_URL",
        "http://localhost:3001"
    )
    AVIATIONSTACK_API_KEY = os.getenv("AVIATIONSTACK_API_KEY", "")
    
    # Google Maps (Optional)
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "")
    
    # Connection settings
    MCP_CONNECTION_TIMEOUT = int(os.getenv("MCP_CONNECTION_TIMEOUT", "5"))
    MCP_REQUEST_TIMEOUT = int(os.getenv("MCP_REQUEST_TIMEOUT", "30"))
    
    @classmethod
    def get_config_dict(cls) -> Dict:
        """Get all MCP configuration as dictionary."""
        return {
            "openmeteo": {
                "server_url": cls.OPENMETEO_MCP_SERVER_URL,
                "enabled": True,
            },
            "aviationstack": {
                "server_url": cls.AVIATIONSTACK_MCP_SERVER_URL,
                "api_key": "***" if cls.AVIATIONSTACK_API_KEY else None,
                "enabled": True,
            },
            "google_maps": {
                "api_key": "***" if cls.GOOGLE_MAPS_API_KEY else None,
                "enabled": bool(cls.GOOGLE_MAPS_API_KEY),
            },
            "timeouts": {
                "connection": cls.MCP_CONNECTION_TIMEOUT,
                "request": cls.MCP_REQUEST_TIMEOUT,
            }
        }
    
    @classmethod
    def validate_config(cls) -> Dict[str, bool]:
        """Validate MCP configuration."""
        return {
            "openmeteo": True,  # Always available (free API)
            "aviationstack": bool(cls.AVIATIONSTACK_API_KEY),
            "google_maps": bool(cls.GOOGLE_MAPS_API_KEY),
        }
