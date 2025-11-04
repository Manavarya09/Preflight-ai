"""
Configuration validation and management for production deployment.
Ensures all required environment variables are set and valid.
"""

import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class ConfigError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


class Config:
    """
    Production configuration with validation.
    All sensitive values must come from environment variables.
    """
    
    # ========== Database Configuration ==========
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")
    
    # ========== MCP Server Configuration ==========
    OPENMETEO_MCP_SERVER_URL: str = os.getenv(
        "OPENMETEO_MCP_SERVER_URL", 
        "http://openmeteo-mcp:3000"
    )
    AVIATIONSTACK_MCP_SERVER_URL: str = os.getenv(
        "AVIATIONSTACK_MCP_SERVER_URL",
        "http://aviationstack-mcp:3001"
    )
    MCP_CONNECTION_TIMEOUT: int = int(os.getenv("MCP_CONNECTION_TIMEOUT", "5"))
    MCP_REQUEST_TIMEOUT: int = int(os.getenv("MCP_REQUEST_TIMEOUT", "30"))
    
    # ========== API Keys (Required) ==========
    AVIATIONSTACK_API_KEY: Optional[str] = os.getenv("AVIATIONSTACK_API_KEY")
    
    # ========== API Keys (Optional) ==========
    GOOGLE_MAPS_API_KEY: Optional[str] = os.getenv("GOOGLE_MAPS_API_KEY")
    TWILIO_ACCOUNT_SID: Optional[str] = os.getenv("TWILIO_ACCOUNT_SID")
    TWILIO_AUTH_TOKEN: Optional[str] = os.getenv("TWILIO_AUTH_TOKEN")
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    
    # ========== Application Settings ==========
    APP_ENV: str = os.getenv("APP_ENV", "production")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # ========== Security Settings ==========
    ALLOWED_ORIGINS: str = os.getenv(
        "ALLOWED_ORIGINS", 
        "http://localhost:3000,http://localhost:8000"
    )
    API_RATE_LIMIT_PER_MINUTE: str = os.getenv("API_RATE_LIMIT_PER_MINUTE", "60/minute")
    
    # ========== Langflow Configuration ==========
    LANGFLOW_FLOW_ID: Optional[str] = os.getenv("LANGFLOW_FLOW_ID")
    LANGFLOW_URL: Optional[str] = os.getenv("LANGFLOW_URL")
    
    @classmethod
    def validate(cls) -> None:
        """
        Validate that all required configuration is present and valid.
        Raises ConfigError if validation fails.
        """
        errors = []
        
        # Check required database configuration
        if not cls.DATABASE_URL:
            errors.append("DATABASE_URL environment variable is required")
        elif not cls.DATABASE_URL.startswith("postgresql://"):
            errors.append("DATABASE_URL must be a valid PostgreSQL connection string")
        
        # Check Redis URL format
        if cls.REDIS_URL and not cls.REDIS_URL.startswith("redis://"):
            errors.append("REDIS_URL must be a valid Redis connection string")
        
        # Check required API keys
        if not cls.AVIATIONSTACK_API_KEY:
            logger.warning(
                "AVIATIONSTACK_API_KEY not set. Flight tracking will rely on MCP server only."
            )
        
        # Validate timeout values
        if cls.MCP_CONNECTION_TIMEOUT <= 0 or cls.MCP_CONNECTION_TIMEOUT > 30:
            errors.append("MCP_CONNECTION_TIMEOUT must be between 1 and 30 seconds")
        
        if cls.MCP_REQUEST_TIMEOUT <= 0 or cls.MCP_REQUEST_TIMEOUT > 300:
            errors.append("MCP_REQUEST_TIMEOUT must be between 1 and 300 seconds")
        
        # Validate APP_ENV
        if cls.APP_ENV not in ["development", "staging", "production"]:
            logger.warning(f"APP_ENV '{cls.APP_ENV}' is not standard. Use development, staging, or production.")
        
        # Validate LOG_LEVEL
        valid_log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if cls.LOG_LEVEL not in valid_log_levels:
            errors.append(f"LOG_LEVEL must be one of: {', '.join(valid_log_levels)}")
        
        # Security checks for production
        if cls.APP_ENV == "production":
            if "*" in cls.ALLOWED_ORIGINS:
                errors.append(
                    "SECURITY: ALLOWED_ORIGINS must not contain '*' in production. "
                    "Specify exact frontend domains."
                )
            
            if not cls.DATABASE_URL.startswith("postgresql://") or "localhost" in cls.DATABASE_URL:
                logger.warning(
                    "SECURITY: DATABASE_URL appears to use localhost in production. "
                    "Ensure you're using a production database."
                )
        
        # Raise error if any validation failed
        if errors:
            error_message = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_message)
            raise ConfigError(error_message)
        
        logger.info("Configuration validation passed")
    
    @classmethod
    def log_config(cls) -> None:
        """Log current configuration (without sensitive values)."""
        logger.info("=== PreFlight AI Configuration ===")
        logger.info(f"Environment: {cls.APP_ENV}")
        logger.info(f"Log Level: {cls.LOG_LEVEL}")
        logger.info(f"Database: {'Configured' if cls.DATABASE_URL else 'Not configured'}")
        logger.info(f"Redis: {'Configured' if cls.REDIS_URL else 'Not configured'}")
        logger.info(f"Open-Meteo MCP: {cls.OPENMETEO_MCP_SERVER_URL}")
        logger.info(f"AviationStack MCP: {cls.AVIATIONSTACK_MCP_SERVER_URL}")
        logger.info(f"AviationStack API Key: {'Set' if cls.AVIATIONSTACK_API_KEY else 'Not set'}")
        logger.info(f"Google Maps API Key: {'Set' if cls.GOOGLE_MAPS_API_KEY else 'Not set (optional)'}")
        logger.info(f"Langflow: {'Configured' if cls.LANGFLOW_FLOW_ID else 'Not configured'}")
        logger.info(f"CORS Allowed Origins: {cls.ALLOWED_ORIGINS}")
        logger.info(f"Rate Limit: {cls.API_RATE_LIMIT_PER_MINUTE}")
        logger.info("=" * 40)


# Validate configuration on module import
try:
    Config.validate()
    Config.log_config()
except ConfigError as e:
    logger.error(f"Configuration error: {e}")
    if os.getenv("APP_ENV") == "production":
        # In production, fail fast if configuration is invalid
        sys.exit(1)
    else:
        # In development, allow startup but log warning
        logger.warning("Continuing despite configuration errors (development mode)")
