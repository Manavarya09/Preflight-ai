-- PreFlight AI Database Schema
-- PostgreSQL 15+

-- ============================================================================
-- EXTENSIONS
-- ============================================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; -- For text search optimization

-- ============================================================================
-- CORE FLIGHT OPERATIONS TABLES
-- ============================================================================

-- Historical flight records with actual outcomes
CREATE TABLE flights_history (
    flight_id VARCHAR(20) PRIMARY KEY,
    origin VARCHAR(4) NOT NULL,
    destination VARCHAR(4) NOT NULL,
    scheduled_departure TIMESTAMP NOT NULL,
    actual_departure TIMESTAMP,
    scheduled_arrival TIMESTAMP NOT NULL,
    actual_arrival TIMESTAMP,
    aircraft_type VARCHAR(10),
    aircraft_registration VARCHAR(10),
    gate VARCHAR(10),
    actual_delay_minutes INTEGER,
    delay_reason TEXT,
    airline_code VARCHAR(3),
    flight_number VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    -- Computed fields
    delay_category VARCHAR(20) GENERATED ALWAYS AS (
        CASE 
            WHEN actual_delay_minutes IS NULL THEN 'UNKNOWN'
            WHEN actual_delay_minutes < 15 THEN 'ON_TIME'
            WHEN actual_delay_minutes < 45 THEN 'MINOR_DELAY'
            WHEN actual_delay_minutes < 120 THEN 'MAJOR_DELAY'
            ELSE 'SEVERE_DELAY'
        END
    ) STORED,
    
    CONSTRAINT valid_airports CHECK (origin != destination),
    CONSTRAINT valid_times CHECK (scheduled_arrival > scheduled_departure)
);

CREATE INDEX idx_flights_dates ON flights_history(scheduled_departure, scheduled_arrival);
CREATE INDEX idx_flights_airports ON flights_history(origin, destination);
CREATE INDEX idx_flights_airline ON flights_history(airline_code);
CREATE INDEX idx_flights_delay ON flights_history(actual_delay_minutes) WHERE actual_delay_minutes IS NOT NULL;

-- ============================================================================
-- PREDICTIONS & ML MODEL TRACKING
-- ============================================================================

-- All ML predictions made by the system
CREATE TABLE predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flight_id VARCHAR(20) NOT NULL REFERENCES flights_history(flight_id) ON DELETE CASCADE,
    model_version_id UUID NOT NULL,
    
    -- Prediction outputs
    delay_probability DECIMAL(5,4) NOT NULL CHECK (delay_probability BETWEEN 0 AND 1),
    predicted_delay_minutes INTEGER NOT NULL CHECK (predicted_delay_minutes >= 0),
    confidence_score DECIMAL(5,4),
    
    -- Prediction inputs (snapshot at prediction time)
    wind_kts DECIMAL(5,2),
    visibility_km DECIMAL(5,2),
    precipitation_mm DECIMAL(5,2),
    temperature_c DECIMAL(5,2),
    atc_status TEXT,
    gate_congestion_level INTEGER,
    
    -- Metadata
    prediction_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    prediction_horizon_minutes INTEGER, -- How far in advance was this prediction made
    
    -- Validation (populated after actual outcome is known)
    actual_delay_minutes INTEGER,
    prediction_error INTEGER, -- actual - predicted
    is_accurate BOOLEAN, -- TRUE if error < 15 minutes
    validated_at TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_predictions_flight ON predictions(flight_id);
CREATE INDEX idx_predictions_model ON predictions(model_version_id);
CREATE INDEX idx_predictions_time ON predictions(prediction_timestamp);
CREATE INDEX idx_predictions_accuracy ON predictions(is_accurate) WHERE validated_at IS NOT NULL;
CREATE INDEX idx_predictions_high_risk ON predictions(delay_probability) WHERE delay_probability >= 0.6;

-- SHAP explanation values for interpretability
CREATE TABLE shap_explanations (
    shap_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL UNIQUE REFERENCES predictions(prediction_id) ON DELETE CASCADE,
    
    -- SHAP values (contribution of each feature)
    crosswind_impact DECIMAL(6,4),
    visibility_impact DECIMAL(6,4),
    atc_impact DECIMAL(6,4),
    gate_congestion_impact DECIMAL(6,4),
    weather_combined_impact DECIMAL(6,4),
    time_of_day_impact DECIMAL(6,4),
    route_impact DECIMAL(6,4),
    
    -- Top contributing factors (for quick lookup)
    primary_factor VARCHAR(50),
    secondary_factor VARCHAR(50),
    tertiary_factor VARCHAR(50),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_shap_prediction ON shap_explanations(prediction_id);

-- ML Model versions tracking
CREATE TABLE model_versions (
    model_version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_number INTEGER NOT NULL UNIQUE,
    model_type VARCHAR(50) NOT NULL, -- 'LSTM_XGBOOST', 'PROPHET', etc.
    model_file_path TEXT NOT NULL,
    
    -- Training information
    training_start_date DATE NOT NULL,
    training_end_date DATE NOT NULL,
    training_samples_count INTEGER NOT NULL,
    validation_samples_count INTEGER NOT NULL,
    
    -- Performance metrics
    accuracy DECIMAL(5,4) NOT NULL,
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    mae DECIMAL(6,2), -- Mean Absolute Error
    rmse DECIMAL(6,2), -- Root Mean Square Error
    
    -- Metadata
    hyperparameters JSONB,
    feature_importance JSONB,
    training_duration_minutes INTEGER,
    is_active BOOLEAN DEFAULT FALSE,
    deployed_at TIMESTAMP,
    deprecated_at TIMESTAMP,
    
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    notes TEXT,
    
    CONSTRAINT valid_dates CHECK (training_end_date >= training_start_date)
);

CREATE INDEX idx_model_active ON model_versions(is_active) WHERE is_active = TRUE;
CREATE INDEX idx_model_accuracy ON model_versions(accuracy DESC);
CREATE INDEX idx_model_created ON model_versions(created_at DESC);

-- Model performance metrics over time
CREATE TABLE model_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_version_id UUID NOT NULL REFERENCES model_versions(model_version_id) ON DELETE CASCADE,
    
    metric_date DATE NOT NULL,
    total_predictions INTEGER NOT NULL DEFAULT 0,
    accurate_predictions INTEGER NOT NULL DEFAULT 0,
    daily_accuracy DECIMAL(5,4) GENERATED ALWAYS AS (
        CASE 
            WHEN total_predictions > 0 THEN accurate_predictions::DECIMAL / total_predictions
            ELSE 0
        END
    ) STORED,
    
    avg_prediction_error DECIMAL(6,2),
    max_prediction_error DECIMAL(6,2),
    
    created_at TIMESTAMP DEFAULT NOW(),
    
    UNIQUE(model_version_id, metric_date)
);

CREATE INDEX idx_metrics_model_date ON model_metrics(model_version_id, metric_date);

-- ============================================================================
-- ALERTS & NOTIFICATIONS
-- ============================================================================

-- System-generated alerts for high-risk flights
CREATE TABLE alerts (
    alert_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    flight_id VARCHAR(20) NOT NULL REFERENCES flights_history(flight_id) ON DELETE CASCADE,
    prediction_id UUID REFERENCES predictions(prediction_id) ON DELETE SET NULL,
    
    -- Alert details
    alert_type VARCHAR(30) NOT NULL, -- 'HIGH_RISK', 'WEATHER_SEVERE', 'ATC_DELAY', etc.
    severity_level INTEGER NOT NULL CHECK (severity_level BETWEEN 1 AND 5), -- 1=low, 5=critical
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    
    -- Status tracking
    status VARCHAR(20) NOT NULL DEFAULT 'ACTIVE', -- 'ACTIVE', 'ACKNOWLEDGED', 'RESOLVED', 'ESCALATED'
    triggered_at TIMESTAMP NOT NULL DEFAULT NOW(),
    acknowledged_at TIMESTAMP,
    acknowledged_by VARCHAR(100),
    resolved_at TIMESTAMP,
    resolved_by VARCHAR(100),
    
    -- Notification flags
    sms_sent BOOLEAN DEFAULT FALSE,
    email_sent BOOLEAN DEFAULT FALSE,
    slack_sent BOOLEAN DEFAULT FALSE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_status_flow CHECK (
        (acknowledged_at IS NULL OR acknowledged_at >= triggered_at) AND
        (resolved_at IS NULL OR resolved_at >= triggered_at)
    )
);

CREATE INDEX idx_alerts_flight ON alerts(flight_id);
CREATE INDEX idx_alerts_status ON alerts(status) WHERE status = 'ACTIVE';
CREATE INDEX idx_alerts_severity ON alerts(severity_level DESC, triggered_at DESC);
CREATE INDEX idx_alerts_time ON alerts(triggered_at DESC);

-- User actions taken in response to alerts
CREATE TABLE alert_actions (
    action_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    alert_id UUID NOT NULL REFERENCES alerts(alert_id) ON DELETE CASCADE,
    
    action_type VARCHAR(30) NOT NULL, -- 'ACKNOWLEDGE', 'ESCALATE', 'COMMENT', 'DISMISS', 'NOTIFY_CREW'
    action_by VARCHAR(100) NOT NULL,
    action_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    
    comment TEXT,
    metadata JSONB, -- Store additional context
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_actions_alert ON alert_actions(alert_id);
CREATE INDEX idx_actions_user ON alert_actions(action_by);

-- ============================================================================
-- WEATHER DATA
-- ============================================================================

-- Historical weather snapshots at prediction time
CREATE TABLE weather_snapshots (
    weather_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL REFERENCES predictions(prediction_id) ON DELETE CASCADE,
    airport_code VARCHAR(4) NOT NULL,
    
    -- Weather conditions
    timestamp TIMESTAMP NOT NULL,
    temperature_c DECIMAL(5,2),
    wind_speed_kts DECIMAL(5,2),
    wind_direction_deg INTEGER CHECK (wind_direction_deg BETWEEN 0 AND 360),
    wind_gust_kts DECIMAL(5,2),
    visibility_km DECIMAL(5,2),
    cloud_coverage_percent INTEGER CHECK (cloud_coverage_percent BETWEEN 0 AND 100),
    precipitation_type VARCHAR(20), -- 'RAIN', 'SNOW', 'SLEET', 'NONE'
    precipitation_mm DECIMAL(5,2),
    pressure_mb DECIMAL(6,2),
    humidity_percent INTEGER CHECK (humidity_percent BETWEEN 0 AND 100),
    
    -- Aviation-specific
    metar_raw TEXT, -- Raw METAR string
    wind_shear_alert BOOLEAN DEFAULT FALSE,
    thunderstorm_nearby BOOLEAN DEFAULT FALSE,
    
    -- API source
    data_source VARCHAR(50) NOT NULL, -- 'OPENWEATHERMAP', 'NOAA', 'FAA'
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_weather_prediction ON weather_snapshots(prediction_id);
CREATE INDEX idx_weather_airport_time ON weather_snapshots(airport_code, timestamp);

-- ============================================================================
-- USER & SYSTEM MANAGEMENT
-- ============================================================================

-- User preferences for notifications and dashboard
CREATE TABLE user_preferences (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(20),
    
    -- Notification preferences
    notify_sms BOOLEAN DEFAULT FALSE,
    notify_email BOOLEAN DEFAULT TRUE,
    notify_slack BOOLEAN DEFAULT FALSE,
    notification_threshold DECIMAL(3,2) DEFAULT 0.70, -- Only notify if delay_prob >= this
    
    -- Dashboard preferences
    dashboard_theme VARCHAR(20) DEFAULT 'dark',
    default_airport VARCHAR(4),
    timezone VARCHAR(50) DEFAULT 'UTC',
    
    -- Access control
    role VARCHAR(20) NOT NULL DEFAULT 'viewer', -- 'admin', 'operator', 'viewer'
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_username ON user_preferences(username);
CREATE INDEX idx_users_role ON user_preferences(role) WHERE is_active = TRUE;

-- System audit logs for compliance
CREATE TABLE audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- What happened
    action_type VARCHAR(50) NOT NULL, -- 'PREDICTION_MADE', 'ALERT_CREATED', 'MODEL_DEPLOYED', etc.
    entity_type VARCHAR(50) NOT NULL, -- 'FLIGHT', 'MODEL', 'USER', 'SYSTEM'
    entity_id VARCHAR(100),
    
    -- Who did it
    user_id UUID REFERENCES user_preferences(user_id) ON DELETE SET NULL,
    username VARCHAR(100),
    ip_address INET,
    
    -- When and where
    timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    endpoint VARCHAR(200), -- API endpoint called
    
    -- Details
    action_details JSONB,
    status VARCHAR(20), -- 'SUCCESS', 'FAILED', 'WARNING'
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_user ON audit_logs(user_id);
CREATE INDEX idx_audit_type ON audit_logs(action_type, timestamp DESC);
CREATE INDEX idx_audit_entity ON audit_logs(entity_type, entity_id);

-- API usage tracking for cost management
CREATE TABLE api_usage_logs (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    api_service VARCHAR(50) NOT NULL, -- 'OPENWEATHERMAP', 'AVIATIONSTACK', 'TWILIO', etc.
    endpoint VARCHAR(200) NOT NULL,
    
    request_timestamp TIMESTAMP NOT NULL DEFAULT NOW(),
    response_status INTEGER, -- HTTP status code
    response_time_ms INTEGER, -- Latency
    
    -- Cost tracking
    credits_used DECIMAL(8,4) DEFAULT 0,
    estimated_cost_usd DECIMAL(8,4) DEFAULT 0,
    
    -- Context
    triggered_by VARCHAR(100), -- Which system component made the call
    flight_id VARCHAR(20),
    
    -- Error tracking
    is_successful BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_api_usage_service ON api_usage_logs(api_service, request_timestamp);
CREATE INDEX idx_api_usage_cost ON api_usage_logs(estimated_cost_usd) WHERE estimated_cost_usd > 0;
CREATE INDEX idx_api_usage_errors ON api_usage_logs(is_successful) WHERE is_successful = FALSE;

-- ============================================================================
-- REPORTS & EXPORTS
-- ============================================================================

-- Metadata for generated reports
CREATE TABLE report_metadata (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    report_type VARCHAR(50) NOT NULL, -- 'DAILY', 'WEEKLY', 'INCIDENT', 'CUSTOM'
    report_title VARCHAR(200) NOT NULL,
    report_date DATE NOT NULL,
    
    -- File information
    file_path TEXT NOT NULL,
    file_format VARCHAR(10) NOT NULL, -- 'PDF', 'CSV', 'XLSX'
    file_size_kb INTEGER,
    
    -- Scope
    start_date DATE,
    end_date DATE,
    airport_filter VARCHAR(4),
    
    -- Generation info
    generated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    generated_by VARCHAR(100),
    generation_duration_seconds INTEGER,
    
    -- Access tracking
    download_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP,
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_reports_type_date ON report_metadata(report_type, report_date DESC);
CREATE INDEX idx_reports_generated ON report_metadata(generated_at DESC);

-- ============================================================================
-- VIEWS FOR COMMON QUERIES
-- ============================================================================

-- Active high-risk flights
CREATE VIEW v_active_high_risk_flights AS
SELECT 
    f.flight_id,
    f.origin,
    f.destination,
    f.scheduled_departure,
    p.delay_probability,
    p.predicted_delay_minutes,
    a.alert_id,
    a.severity_level,
    a.status AS alert_status
FROM flights_history f
JOIN predictions p ON f.flight_id = p.flight_id
LEFT JOIN alerts a ON f.flight_id = a.flight_id AND a.status = 'ACTIVE'
WHERE p.prediction_timestamp = (
    SELECT MAX(prediction_timestamp) 
    FROM predictions p2 
    WHERE p2.flight_id = f.flight_id
)
AND p.delay_probability >= 0.6
AND f.scheduled_departure > NOW()
ORDER BY p.delay_probability DESC, f.scheduled_departure;

-- Model accuracy dashboard
CREATE VIEW v_model_accuracy_summary AS
SELECT 
    mv.model_version_id,
    mv.version_number,
    mv.model_type,
    mv.accuracy AS training_accuracy,
    COUNT(p.prediction_id) AS total_predictions,
    COUNT(p.prediction_id) FILTER (WHERE p.is_accurate = TRUE) AS accurate_predictions,
    ROUND(
        COUNT(p.prediction_id) FILTER (WHERE p.is_accurate = TRUE)::DECIMAL / 
        NULLIF(COUNT(p.prediction_id), 0), 
        4
    ) AS production_accuracy,
    AVG(ABS(p.prediction_error)) AS avg_absolute_error,
    mv.deployed_at
FROM model_versions mv
LEFT JOIN predictions p ON mv.model_version_id = p.model_version_id AND p.validated_at IS NOT NULL
WHERE mv.is_active = TRUE OR mv.deployed_at > NOW() - INTERVAL '30 days'
GROUP BY mv.model_version_id, mv.version_number, mv.model_type, mv.accuracy, mv.deployed_at
ORDER BY mv.deployed_at DESC;

-- Daily operations summary
CREATE VIEW v_daily_operations_summary AS
SELECT 
    DATE(f.scheduled_departure) AS operation_date,
    COUNT(DISTINCT f.flight_id) AS total_flights,
    COUNT(DISTINCT p.prediction_id) AS predictions_made,
    COUNT(DISTINCT a.alert_id) AS alerts_triggered,
    COUNT(DISTINCT a.alert_id) FILTER (WHERE a.severity_level >= 4) AS critical_alerts,
    AVG(p.delay_probability) AS avg_delay_probability,
    AVG(f.actual_delay_minutes) AS avg_actual_delay,
    COUNT(f.flight_id) FILTER (WHERE f.actual_delay_minutes >= 15) AS delayed_flights,
    ROUND(
        COUNT(f.flight_id) FILTER (WHERE f.actual_delay_minutes >= 15)::DECIMAL / 
        NULLIF(COUNT(f.flight_id), 0) * 100,
        2
    ) AS delay_percentage
FROM flights_history f
LEFT JOIN predictions p ON f.flight_id = p.flight_id
LEFT JOIN alerts a ON f.flight_id = a.flight_id
WHERE f.scheduled_departure >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY DATE(f.scheduled_departure)
ORDER BY operation_date DESC;

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Automatically update 'updated_at' timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_flights_updated_at BEFORE UPDATE ON flights_history
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_alerts_updated_at BEFORE UPDATE ON alerts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON user_preferences
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Validate prediction after actual outcome is known
CREATE OR REPLACE FUNCTION validate_prediction()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.actual_delay_minutes IS NOT NULL AND OLD.actual_delay_minutes IS NULL THEN
        -- Calculate prediction error
        NEW.prediction_error := NEW.actual_delay_minutes - NEW.predicted_delay_minutes;
        
        -- Mark as accurate if error is within 15 minutes
        NEW.is_accurate := ABS(NEW.prediction_error) <= 15;
        
        -- Set validation timestamp
        NEW.validated_at := NOW();
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER validate_prediction_trigger BEFORE UPDATE ON predictions
    FOR EACH ROW EXECUTE FUNCTION validate_prediction();

-- ============================================================================
-- LOCATION AND GEOCODING CACHE TABLES
-- ============================================================================

-- Cached airport location data from Google Maps
CREATE TABLE airport_locations (
    airport_code VARCHAR(4) PRIMARY KEY,
    airport_name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    country VARCHAR(100),
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    formatted_address TEXT,
    google_place_id VARCHAR(255),
    timezone_id VARCHAR(100),
    timezone_name VARCHAR(100),
    utc_offset_seconds INTEGER,
    elevation_meters INTEGER,
    source VARCHAR(50) DEFAULT 'GOOGLE_MAPS',
    last_verified TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_latitude CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT valid_longitude CHECK (longitude BETWEEN -180 AND 180),
    CONSTRAINT valid_airport_code CHECK (LENGTH(airport_code) = 3 OR LENGTH(airport_code) = 4)
);

CREATE INDEX idx_airport_location_coords ON airport_locations(latitude, longitude);
CREATE INDEX idx_airport_location_city ON airport_locations(city);
CREATE INDEX idx_airport_location_country ON airport_locations(country);
CREATE INDEX idx_airport_place_id ON airport_locations(google_place_id);

-- Cached route distances and travel times
CREATE TABLE route_distances (
    id SERIAL PRIMARY KEY,
    origin_airport VARCHAR(4) NOT NULL,
    destination_airport VARCHAR(4) NOT NULL,
    distance_meters BIGINT NOT NULL,
    distance_km DECIMAL(10, 2) GENERATED ALWAYS AS (distance_meters / 1000.0) STORED,
    distance_nm DECIMAL(10, 2) GENERATED ALWAYS AS (distance_meters / 1852.0) STORED,
    great_circle_distance_km DECIMAL(10, 2),
    average_flight_duration_minutes INTEGER,
    source VARCHAR(50) DEFAULT 'GOOGLE_MAPS',
    last_calculated TIMESTAMP DEFAULT NOW(),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT valid_distance CHECK (distance_meters > 0),
    CONSTRAINT valid_airports_route CHECK (origin_airport != destination_airport),
    CONSTRAINT unique_route UNIQUE (origin_airport, destination_airport)
);

CREATE INDEX idx_route_origin ON route_distances(origin_airport);
CREATE INDEX idx_route_destination ON route_distances(destination_airport);
CREATE INDEX idx_route_distance ON route_distances(distance_km);

-- Geocoding cache for general addresses
CREATE TABLE geocoding_cache (
    id SERIAL PRIMARY KEY,
    search_query TEXT NOT NULL,
    search_query_hash VARCHAR(64) NOT NULL UNIQUE,
    latitude DECIMAL(10, 8) NOT NULL,
    longitude DECIMAL(11, 8) NOT NULL,
    formatted_address TEXT,
    google_place_id VARCHAR(255),
    location_type VARCHAR(50),
    address_components JSONB,
    viewport JSONB,
    cache_hits INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW(),
    expires_at TIMESTAMP NOT NULL,
    
    CONSTRAINT valid_geocode_lat CHECK (latitude BETWEEN -90 AND 90),
    CONSTRAINT valid_geocode_lng CHECK (longitude BETWEEN -180 AND 180)
);

CREATE INDEX idx_geocoding_hash ON geocoding_cache(search_query_hash);
CREATE INDEX idx_geocoding_expiry ON geocoding_cache(expires_at);
CREATE INDEX idx_geocoding_coords ON geocoding_cache(latitude, longitude);

-- ============================================================================
-- LOCATION-RELATED VIEWS
-- ============================================================================

-- View for valid, recently verified airport locations
CREATE OR REPLACE VIEW v_verified_airport_locations AS
SELECT 
    airport_code,
    airport_name,
    city,
    country,
    latitude,
    longitude,
    timezone_id,
    timezone_name,
    EXTRACT(EPOCH FROM (NOW() - last_verified)) / 86400 AS days_since_verification
FROM airport_locations
WHERE last_verified > NOW() - INTERVAL '90 days'
ORDER BY airport_code;

-- View for route statistics with distances
CREATE OR REPLACE VIEW v_route_analysis AS
SELECT 
    rd.origin_airport,
    rd.destination_airport,
    rd.distance_km,
    rd.distance_nm,
    rd.average_flight_duration_minutes,
    ao.city AS origin_city,
    ao.country AS origin_country,
    ad.city AS destination_city,
    ad.country AS destination_country,
    COUNT(fh.flight_id) AS historical_flights,
    AVG(fh.actual_delay_minutes) AS avg_delay_minutes,
    STDDEV(fh.actual_delay_minutes) AS delay_stddev
FROM route_distances rd
LEFT JOIN airport_locations ao ON rd.origin_airport = ao.airport_code
LEFT JOIN airport_locations ad ON rd.destination_airport = ad.airport_code
LEFT JOIN flights_history fh ON rd.origin_airport = fh.origin 
    AND rd.destination_airport = fh.destination
GROUP BY rd.id, ao.city, ao.country, ad.city, ad.country;

-- ============================================================================
-- LOCATION-RELATED TRIGGERS
-- ============================================================================

CREATE TRIGGER update_airport_locations_updated_at BEFORE UPDATE ON airport_locations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_route_distances_updated_at BEFORE UPDATE ON route_distances
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- INITIAL DATA
-- ============================================================================

-- Create default admin user
INSERT INTO user_preferences (username, email, role, notify_email) 
VALUES ('admin', 'admin@preflight.ai', 'admin', TRUE)
ON CONFLICT (username) DO NOTHING;

-- ============================================================================
-- GRANTS (for application user)
-- ============================================================================

-- Create application user if needed
-- CREATE USER preflight_app WITH PASSWORD 'secure_password';

-- Grant permissions
-- GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO preflight_app;
-- GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO preflight_app;

-- ============================================================================
-- COMMENTS FOR DOCUMENTATION
-- ============================================================================

COMMENT ON TABLE flights_history IS 'Historical flight records with actual outcomes for validation';
COMMENT ON TABLE predictions IS 'All ML predictions with inputs, outputs, and validation results';
COMMENT ON TABLE shap_explanations IS 'SHAP values explaining feature contributions to predictions';
COMMENT ON TABLE model_versions IS 'Tracking of ML model versions and their performance metrics';
COMMENT ON TABLE alerts IS 'System-generated alerts for high-risk flights requiring attention';
COMMENT ON TABLE weather_snapshots IS 'Historical weather data captured at prediction time';
COMMENT ON TABLE audit_logs IS 'Complete audit trail for compliance and debugging';
COMMENT ON TABLE api_usage_logs IS 'Tracking external API calls for cost management';

COMMENT ON COLUMN predictions.prediction_horizon_minutes IS 'How many minutes before departure was this prediction made';
COMMENT ON COLUMN predictions.is_accurate IS 'TRUE if prediction error is within ±15 minutes of actual delay';
COMMENT ON COLUMN alerts.severity_level IS '1=Low, 2=Medium, 3=High, 4=Critical, 5=Emergency';

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
