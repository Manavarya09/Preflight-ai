"""
SQLAlchemy models for PreFlight AI database
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
    Numeric,
    ForeignKey,
    CheckConstraint,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB, INET
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base = declarative_base()


class FlightHistory(Base):
    """Historical flight records with actual outcomes"""

    __tablename__ = "flights_history"

    flight_id = Column(String(20), primary_key=True)
    origin = Column(String(4), nullable=False)
    destination = Column(String(4), nullable=False)
    scheduled_departure = Column(DateTime, nullable=False)
    actual_departure = Column(DateTime)
    scheduled_arrival = Column(DateTime, nullable=False)
    actual_arrival = Column(DateTime)
    aircraft_type = Column(String(10))
    aircraft_registration = Column(String(10))
    gate = Column(String(10))
    actual_delay_minutes = Column(Integer)
    delay_reason = Column(Text)
    airline_code = Column(String(3))
    flight_number = Column(String(10))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    predictions = relationship("Prediction", back_populates="flight", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="flight", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("origin != destination", name="valid_airports"),
        CheckConstraint("scheduled_arrival > scheduled_departure", name="valid_times"),
        Index("idx_flights_dates", "scheduled_departure", "scheduled_arrival"),
        Index("idx_flights_airports", "origin", "destination"),
        Index("idx_flights_airline", "airline_code"),
    )

    def __repr__(self):
        return f"<Flight {self.flight_id}: {self.origin}→{self.destination}>"


class ModelVersion(Base):
    """ML model versions and their performance metrics"""

    __tablename__ = "model_versions"

    model_version_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    version_number = Column(Integer, nullable=False, unique=True)
    model_type = Column(String(50), nullable=False)
    model_file_path = Column(Text, nullable=False)

    # Training information
    training_start_date = Column(DateTime, nullable=False)
    training_end_date = Column(DateTime, nullable=False)
    training_samples_count = Column(Integer, nullable=False)
    validation_samples_count = Column(Integer, nullable=False)

    # Performance metrics
    accuracy = Column(Numeric(5, 4), nullable=False)
    precision_score = Column(Numeric(5, 4))
    recall_score = Column(Numeric(5, 4))
    f1_score = Column(Numeric(5, 4))
    mae = Column(Numeric(6, 2))  # Mean Absolute Error
    rmse = Column(Numeric(6, 2))  # Root Mean Square Error

    # Metadata
    hyperparameters = Column(JSONB)
    feature_importance = Column(JSONB)
    training_duration_minutes = Column(Integer)
    is_active = Column(Boolean, default=False)
    deployed_at = Column(DateTime)
    deprecated_at = Column(DateTime)

    created_by = Column(String(100))
    created_at = Column(DateTime, default=func.now())
    notes = Column(Text)

    # Relationships
    predictions = relationship("Prediction", back_populates="model_version")
    metrics = relationship("ModelMetric", back_populates="model_version", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("training_end_date >= training_start_date", name="valid_training_dates"),
        Index("idx_model_accuracy", "accuracy", postgresql_using="btree", postgresql_order_by="accuracy DESC"),
        Index("idx_model_created", "created_at", postgresql_using="btree", postgresql_order_by="created_at DESC"),
    )

    def __repr__(self):
        return f"<ModelVersion v{self.version_number} ({self.model_type}): {self.accuracy}>"


class Prediction(Base):
    """All ML predictions made by the system"""

    __tablename__ = "predictions"

    prediction_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    flight_id = Column(String(20), ForeignKey("flights_history.flight_id", ondelete="CASCADE"), nullable=False)
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.model_version_id"), nullable=False)

    # Prediction outputs
    delay_probability = Column(Numeric(5, 4), nullable=False)
    predicted_delay_minutes = Column(Integer, nullable=False)
    confidence_score = Column(Numeric(5, 4))

    # Prediction inputs (snapshot at prediction time)
    wind_kts = Column(Numeric(5, 2))
    visibility_km = Column(Numeric(5, 2))
    precipitation_mm = Column(Numeric(5, 2))
    temperature_c = Column(Numeric(5, 2))
    atc_status = Column(Text)
    gate_congestion_level = Column(Integer)

    # Metadata
    prediction_timestamp = Column(DateTime, nullable=False, default=func.now())
    prediction_horizon_minutes = Column(Integer)

    # Validation
    actual_delay_minutes = Column(Integer)
    prediction_error = Column(Integer)
    is_accurate = Column(Boolean)
    validated_at = Column(DateTime)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    flight = relationship("FlightHistory", back_populates="predictions")
    model_version = relationship("ModelVersion", back_populates="predictions")
    shap_explanation = relationship("ShapExplanation", back_populates="prediction", uselist=False, cascade="all, delete-orphan")
    weather_snapshots = relationship("WeatherSnapshot", back_populates="prediction", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="prediction")

    __table_args__ = (
        CheckConstraint("delay_probability BETWEEN 0 AND 1", name="valid_probability"),
        CheckConstraint("predicted_delay_minutes >= 0", name="valid_delay"),
        Index("idx_predictions_flight", "flight_id"),
        Index("idx_predictions_model", "model_version_id"),
        Index("idx_predictions_time", "prediction_timestamp"),
    )

    def __repr__(self):
        return f"<Prediction {self.flight_id}: {float(self.delay_probability):.2%} delay>"


class ShapExplanation(Base):
    """SHAP values explaining feature contributions to predictions"""

    __tablename__ = "shap_explanations"

    shap_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.prediction_id", ondelete="CASCADE"), nullable=False, unique=True)

    # SHAP values
    crosswind_impact = Column(Numeric(6, 4))
    visibility_impact = Column(Numeric(6, 4))
    atc_impact = Column(Numeric(6, 4))
    gate_congestion_impact = Column(Numeric(6, 4))
    weather_combined_impact = Column(Numeric(6, 4))
    time_of_day_impact = Column(Numeric(6, 4))
    route_impact = Column(Numeric(6, 4))

    # Top factors
    primary_factor = Column(String(50))
    secondary_factor = Column(String(50))
    tertiary_factor = Column(String(50))

    created_at = Column(DateTime, default=func.now())

    # Relationships
    prediction = relationship("Prediction", back_populates="shap_explanation")

    def __repr__(self):
        return f"<ShapExplanation for {self.prediction_id}: {self.primary_factor}>"


class ModelMetric(Base):
    """Model performance metrics over time"""

    __tablename__ = "model_metrics"

    metric_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    model_version_id = Column(UUID(as_uuid=True), ForeignKey("model_versions.model_version_id", ondelete="CASCADE"), nullable=False)

    metric_date = Column(DateTime, nullable=False)
    total_predictions = Column(Integer, nullable=False, default=0)
    accurate_predictions = Column(Integer, nullable=False, default=0)
    avg_prediction_error = Column(Numeric(6, 2))
    max_prediction_error = Column(Numeric(6, 2))

    created_at = Column(DateTime, default=func.now())

    # Relationships
    model_version = relationship("ModelVersion", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint("model_version_id", "metric_date", name="uq_model_date"),
        Index("idx_metrics_model_date", "model_version_id", "metric_date"),
    )

    def __repr__(self):
        return f"<ModelMetric {self.metric_date}: {self.accurate_predictions}/{self.total_predictions}>"


class Alert(Base):
    """System-generated alerts for high-risk flights"""

    __tablename__ = "alerts"

    alert_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    flight_id = Column(String(20), ForeignKey("flights_history.flight_id", ondelete="CASCADE"), nullable=False)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.prediction_id", ondelete="SET NULL"))

    # Alert details
    alert_type = Column(String(30), nullable=False)
    severity_level = Column(Integer, nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)

    # Status tracking
    status = Column(String(20), nullable=False, default="ACTIVE")
    triggered_at = Column(DateTime, nullable=False, default=func.now())
    acknowledged_at = Column(DateTime)
    acknowledged_by = Column(String(100))
    resolved_at = Column(DateTime)
    resolved_by = Column(String(100))

    # Notification flags
    sms_sent = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    slack_sent = Column(Boolean, default=False)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    flight = relationship("FlightHistory", back_populates="alerts")
    prediction = relationship("Prediction", back_populates="alerts")
    actions = relationship("AlertAction", back_populates="alert", cascade="all, delete-orphan")

    __table_args__ = (
        CheckConstraint("severity_level BETWEEN 1 AND 5", name="valid_severity"),
        Index("idx_alerts_flight", "flight_id"),
        Index("idx_alerts_severity", "severity_level", "triggered_at", postgresql_order_by=["severity_level DESC", "triggered_at DESC"]),
        Index("idx_alerts_time", "triggered_at", postgresql_order_by="triggered_at DESC"),
    )

    def __repr__(self):
        return f"<Alert {self.flight_id}: {self.alert_type} (L{self.severity_level})>"


class AlertAction(Base):
    """User actions taken in response to alerts"""

    __tablename__ = "alert_actions"

    action_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    alert_id = Column(UUID(as_uuid=True), ForeignKey("alerts.alert_id", ondelete="CASCADE"), nullable=False)

    action_type = Column(String(30), nullable=False)
    action_by = Column(String(100), nullable=False)
    action_timestamp = Column(DateTime, nullable=False, default=func.now())

    comment = Column(Text)
    metadata = Column(JSONB)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    alert = relationship("Alert", back_populates="actions")

    __table_args__ = (
        Index("idx_actions_alert", "alert_id"),
        Index("idx_actions_user", "action_by"),
    )

    def __repr__(self):
        return f"<AlertAction {self.action_type} by {self.action_by}>"


class WeatherSnapshot(Base):
    """Historical weather data captured at prediction time"""

    __tablename__ = "weather_snapshots"

    weather_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    prediction_id = Column(UUID(as_uuid=True), ForeignKey("predictions.prediction_id", ondelete="CASCADE"), nullable=False)
    airport_code = Column(String(4), nullable=False)

    # Weather conditions
    timestamp = Column(DateTime, nullable=False)
    temperature_c = Column(Numeric(5, 2))
    wind_speed_kts = Column(Numeric(5, 2))
    wind_direction_deg = Column(Integer)
    wind_gust_kts = Column(Numeric(5, 2))
    visibility_km = Column(Numeric(5, 2))
    cloud_coverage_percent = Column(Integer)
    precipitation_type = Column(String(20))
    precipitation_mm = Column(Numeric(5, 2))
    pressure_mb = Column(Numeric(6, 2))
    humidity_percent = Column(Integer)

    # Aviation-specific
    metar_raw = Column(Text)
    wind_shear_alert = Column(Boolean, default=False)
    thunderstorm_nearby = Column(Boolean, default=False)

    # API source
    data_source = Column(String(50), nullable=False)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    prediction = relationship("Prediction", back_populates="weather_snapshots")

    __table_args__ = (
        CheckConstraint("wind_direction_deg BETWEEN 0 AND 360", name="valid_wind_direction"),
        CheckConstraint("cloud_coverage_percent BETWEEN 0 AND 100", name="valid_cloud_coverage"),
        CheckConstraint("humidity_percent BETWEEN 0 AND 100", name="valid_humidity"),
        Index("idx_weather_prediction", "prediction_id"),
        Index("idx_weather_airport_time", "airport_code", "timestamp"),
    )

    def __repr__(self):
        return f"<WeatherSnapshot {self.airport_code} @ {self.timestamp}>"


class UserPreference(Base):
    """User preferences for notifications and dashboard"""

    __tablename__ = "user_preferences"

    user_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))
    username = Column(String(100), nullable=False, unique=True)
    email = Column(String(255), nullable=False)
    phone_number = Column(String(20))

    # Notification preferences
    notify_sms = Column(Boolean, default=False)
    notify_email = Column(Boolean, default=True)
    notify_slack = Column(Boolean, default=False)
    notification_threshold = Column(Numeric(3, 2), default=Decimal("0.70"))

    # Dashboard preferences
    dashboard_theme = Column(String(20), default="dark")
    default_airport = Column(String(4))
    timezone = Column(String(50), default="UTC")

    # Access control
    role = Column(String(20), nullable=False, default="viewer")
    is_active = Column(Boolean, default=True)

    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    audit_logs = relationship("AuditLog", back_populates="user")

    __table_args__ = (
        Index("idx_users_username", "username"),
    )

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class AuditLog(Base):
    """System audit logs for compliance and debugging"""

    __tablename__ = "audit_logs"

    log_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))

    # What happened
    action_type = Column(String(50), nullable=False)
    entity_type = Column(String(50), nullable=False)
    entity_id = Column(String(100))

    # Who did it
    user_id = Column(UUID(as_uuid=True), ForeignKey("user_preferences.user_id", ondelete="SET NULL"))
    username = Column(String(100))
    ip_address = Column(INET)

    # When and where
    timestamp = Column(DateTime, nullable=False, default=func.now())
    endpoint = Column(String(200))

    # Details
    action_details = Column(JSONB)
    status = Column(String(20))
    error_message = Column(Text)

    created_at = Column(DateTime, default=func.now())

    # Relationships
    user = relationship("UserPreference", back_populates="audit_logs")

    __table_args__ = (
        Index("idx_audit_timestamp", "timestamp", postgresql_order_by="timestamp DESC"),
        Index("idx_audit_user", "user_id"),
        Index("idx_audit_type", "action_type", "timestamp", postgresql_order_by=["action_type", "timestamp DESC"]),
        Index("idx_audit_entity", "entity_type", "entity_id"),
    )

    def __repr__(self):
        return f"<AuditLog {self.action_type} @ {self.timestamp}>"


class ApiUsageLog(Base):
    """API usage tracking for cost management"""

    __tablename__ = "api_usage_logs"

    usage_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))

    api_service = Column(String(50), nullable=False)
    endpoint = Column(String(200), nullable=False)

    request_timestamp = Column(DateTime, nullable=False, default=func.now())
    response_status = Column(Integer)
    response_time_ms = Column(Integer)

    # Cost tracking
    credits_used = Column(Numeric(8, 4), default=Decimal("0"))
    estimated_cost_usd = Column(Numeric(8, 4), default=Decimal("0"))

    # Context
    triggered_by = Column(String(100))
    flight_id = Column(String(20))

    # Error tracking
    is_successful = Column(Boolean, default=True)
    error_message = Column(Text)

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_api_usage_service", "api_service", "request_timestamp"),
    )

    def __repr__(self):
        return f"<ApiUsageLog {self.api_service} @ {self.request_timestamp}>"


class ReportMetadata(Base):
    """Metadata for generated reports"""

    __tablename__ = "report_metadata"

    report_id = Column(UUID(as_uuid=True), primary_key=True, server_default=text("uuid_generate_v4()"))

    report_type = Column(String(50), nullable=False)
    report_title = Column(String(200), nullable=False)
    report_date = Column(DateTime, nullable=False)

    # File information
    file_path = Column(Text, nullable=False)
    file_format = Column(String(10), nullable=False)
    file_size_kb = Column(Integer)

    # Scope
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    airport_filter = Column(String(4))

    # Generation info
    generated_at = Column(DateTime, nullable=False, default=func.now())
    generated_by = Column(String(100))
    generation_duration_seconds = Column(Integer)

    # Access tracking
    download_count = Column(Integer, default=0)
    last_accessed = Column(DateTime)

    created_at = Column(DateTime, default=func.now())

    __table_args__ = (
        Index("idx_reports_type_date", "report_type", "report_date", postgresql_order_by=["report_type", "report_date DESC"]),
        Index("idx_reports_generated", "generated_at", postgresql_order_by="generated_at DESC"),
    )

    def __repr__(self):
        return f"<ReportMetadata {self.report_type} - {self.report_date}>"


class AirportLocation(Base):
    """Cached airport location data from Google Maps"""

    __tablename__ = "airport_locations"

    airport_code = Column(String(4), primary_key=True)
    airport_name = Column(String(255), nullable=False)
    city = Column(String(100))
    country = Column(String(100))
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    formatted_address = Column(Text)
    google_place_id = Column(String(255))
    timezone_id = Column(String(100))
    timezone_name = Column(String(100))
    utc_offset_seconds = Column(Integer)
    elevation_meters = Column(Integer)
    source = Column(String(50), default="GOOGLE_MAPS")
    last_verified = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="valid_latitude"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="valid_longitude"),
        CheckConstraint("LENGTH(airport_code) = 3 OR LENGTH(airport_code) = 4", name="valid_airport_code"),
        Index("idx_airport_location_coords", "latitude", "longitude"),
        Index("idx_airport_location_city", "city"),
        Index("idx_airport_location_country", "country"),
        Index("idx_airport_place_id", "google_place_id"),
    )

    def __repr__(self):
        return f"<AirportLocation {self.airport_code} - {self.airport_name}>"


class RouteDistance(Base):
    """Cached route distances and travel times"""

    __tablename__ = "route_distances"

    id = Column(Integer, primary_key=True, autoincrement=True)
    origin_airport = Column(String(4), nullable=False)
    destination_airport = Column(String(4), nullable=False)
    distance_meters = Column(Integer, nullable=False)
    great_circle_distance_km = Column(Numeric(10, 2))
    average_flight_duration_minutes = Column(Integer)
    source = Column(String(50), default="GOOGLE_MAPS")
    last_calculated = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("distance_meters > 0", name="valid_distance"),
        CheckConstraint("origin_airport != destination_airport", name="valid_airports_route"),
        UniqueConstraint("origin_airport", "destination_airport", name="unique_route"),
        Index("idx_route_origin", "origin_airport"),
        Index("idx_route_destination", "destination_airport"),
    )

    def __repr__(self):
        return f"<RouteDistance {self.origin_airport} -> {self.destination_airport}>"


class GeocodingCache(Base):
    """Geocoding cache for general addresses"""

    __tablename__ = "geocoding_cache"

    id = Column(Integer, primary_key=True, autoincrement=True)
    search_query = Column(Text, nullable=False)
    search_query_hash = Column(String(64), nullable=False, unique=True)
    latitude = Column(Numeric(10, 8), nullable=False)
    longitude = Column(Numeric(11, 8), nullable=False)
    formatted_address = Column(Text)
    google_place_id = Column(String(255))
    location_type = Column(String(50))
    address_components = Column(JSONB)
    viewport = Column(JSONB)
    cache_hits = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)

    __table_args__ = (
        CheckConstraint("latitude BETWEEN -90 AND 90", name="valid_geocode_lat"),
        CheckConstraint("longitude BETWEEN -180 AND 180", name="valid_geocode_lng"),
        Index("idx_geocoding_hash", "search_query_hash"),
        Index("idx_geocoding_expiry", "expires_at"),
        Index("idx_geocoding_coords", "latitude", "longitude"),
    )

    def __repr__(self):
        return f"<GeocodingCache {self.search_query[:50]}>"
