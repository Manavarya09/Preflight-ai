"""
Database package for PreFlight AI
"""
from database.connection import (
    engine,
    SessionLocal,
    redis_client,
    get_db,
    get_db_context,
    get_redis,
    check_connections,
)
from database.models import (
    Base,
    FlightHistory,
    ModelVersion,
    Prediction,
    ShapExplanation,
    Alert,
    AlertAction,
    WeatherSnapshot,
    UserPreference,
    AuditLog,
    ApiUsageLog,
    ReportMetadata,
)

__all__ = [
    # Connection
    "engine",
    "SessionLocal",
    "redis_client",
    "get_db",
    "get_db_context",
    "get_redis",
    "check_connections",
    # Models
    "Base",
    "FlightHistory",
    "ModelVersion",
    "Prediction",
    "ShapExplanation",
    "Alert",
    "AlertAction",
    "WeatherSnapshot",
    "UserPreference",
    "AuditLog",
    "ApiUsageLog",
    "ReportMetadata",
]
