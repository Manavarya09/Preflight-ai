from datetime import datetime, timedelta
from typing import List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.models.explain import explain_prediction
from app.models.predictor import predict_delay
from app.schemas.flight import FlightRecord
from app.services.langflow_client import generate_explanation

# Database imports
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db, check_connections
from database.models import (
    FlightHistory,
    Prediction,
    ShapExplanation,
    Alert,
    WeatherSnapshot,
)

# MCP Client imports (with fallback to legacy API clients)
try:
    from mcp_clients import (
        OpenMeteoMCPClient,
        OpenMeteoMCPError,
        AviationStackMCPClient,
        AviationStackMCPError,
        GoogleMapsMCPClient,
        GoogleMapsMCPError,
    )
    from mcp_clients.mcp_config import MCPConfig
    USE_MCP_CLIENTS = True
except ImportError:
    # Fallback to legacy API clients
    from external_apis import (
        AviationStackClient,
        AviationStackError,
        OpenMeteoClient,
        OpenMeteoError,
    )
    USE_MCP_CLIENTS = False
    print("Warning: MCP clients not available, using legacy API clients")

app = FastAPI(
    title="PreFlight AI API",
    version="2.0",
    description="Intelligent flight delay prediction with real-time weather and flight tracking",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize MCP clients or legacy API clients
if USE_MCP_CLIENTS:
    # Initialize MCP clients with configuration
    weather_client = OpenMeteoMCPClient(
        mcp_server_url=MCPConfig.OPENMETEO_MCP_SERVER_URL
    )
    aviation_client = AviationStackMCPClient(
        mcp_server_url=MCPConfig.AVIATIONSTACK_MCP_SERVER_URL,
        api_key=MCPConfig.AVIATIONSTACK_API_KEY
    )
    googlemaps_client = GoogleMapsMCPClient(
        api_key=MCPConfig.GOOGLE_MAPS_API_KEY
    )
    print("✓ MCP clients initialized successfully")
else:
    # Fallback to legacy API clients
    aviation_client = AviationStackClient()
    weather_client = OpenMeteoClient()
    googlemaps_client = None
    print("✓ Legacy API clients initialized")


@app.get("/")
def root():
    """Root endpoint with service status."""
    services_status = {
        "database": "connected",
        "weather_api": "Open-Meteo MCP" if USE_MCP_CLIENTS else "Open-Meteo Direct",
        "flight_api": "AviationStack MCP" if USE_MCP_CLIENTS else "AviationStack Direct",
        "google_maps": "Enabled (MCP)" if (USE_MCP_CLIENTS and googlemaps_client and googlemaps_client.is_enabled()) else "Disabled",
    }
    
    return {
        "message": "PreFlight AI backend running",
        "version": "2.0",
        "architecture": "MCP-based" if USE_MCP_CLIENTS else "Legacy",
        "services": services_status,
    }


@app.get("/health")
def health_check(db: Session = Depends(get_db)):
    """Comprehensive health check for all services."""
    health_status = check_connections()
    
    # Add MCP client health checks
    if USE_MCP_CLIENTS:
        health_status["mcp_openmeteo"] = weather_client.use_mcp
        health_status["mcp_aviationstack"] = aviation_client.use_mcp
        health_status["mcp_googlemaps"] = googlemaps_client.is_enabled() if googlemaps_client else False
        
    return {
        "status": "healthy" if all([v for k, v in health_status.items() if k.startswith("db_")]) else "degraded",
        "timestamp": datetime.now().isoformat(),
        "architecture": "MCP-based" if USE_MCP_CLIENTS else "Legacy",
        "services": health_status,
    }


@app.get("/flights")
def get_flights():
    return [
        {
            "flight_id": "EK230",
            "origin": "DXB",
            "dest": "LHR",
            "delay_prob": 0.78,
            "status": "likely delayed",
        },
        {
            "flight_id": "AI101",
            "origin": "DEL",
            "dest": "DXB",
            "delay_prob": 0.21,
            "status": "on-time",
        },
    ]


@app.post("/score")
def score_flight(record: FlightRecord, background_tasks: BackgroundTasks):
    features = {
        "wind": record.weather.get("wind_kts", 0),
        "visibility": record.weather.get("visibility_km", 10),
        "atc": len(record.atc),
    }
    prob, delay = predict_delay(features)
    shap = explain_prediction(features)
    explanation = generate_explanation(shap)
    return {
        "flight_id": record.flight_id,
        "delay_prob": prob,
        "predicted_delay_minutes": delay,
        "shap": shap,
        "explanation": explanation,
    }


@app.get("/insights")
def insights():
    return generate_explanation(
        {"crosswind": 0.2, "gate_congestion": 0.17, "route_delay": 0.14}
    )


# ========== WEATHER API ENDPOINTS ==========


@app.get("/weather/current/{airport_code}")
def get_current_weather(airport_code: str, db: Session = Depends(get_db)):
    """
    Get current weather conditions for an airport.

    Args:
        airport_code: IATA airport code (e.g., DXB, LHR, JFK)
    """
    try:
        weather_data = weather_client.get_current_weather(airport_code)

        # Store weather snapshot in database
        weather_snapshot = WeatherSnapshot(
            airport_code=airport_code.upper(),
            observation_time=datetime.now(),
            temperature_c=weather_data["temperature_c"],
            wind_speed_kts=weather_data["wind_speed_kts"],
            wind_direction_deg=weather_data["wind_direction_deg"],
            visibility_km=weather_data["visibility_km"],
            cloud_coverage_percent=weather_data["cloud_coverage_percent"],
            precipitation_type=weather_data["precipitation_type"],
            precipitation_mm=weather_data["precipitation_mm"],
            pressure_mb=weather_data["pressure_mb"],
            humidity_percent=weather_data["humidity_percent"],
            data_source=weather_data["data_source"],
        )
        db.add(weather_snapshot)
        db.commit()

        return weather_data

    except Exception as e:
        # Handle both MCP and legacy errors
        error_msg = f"Weather API error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/weather/forecast/{airport_code}")
def get_weather_forecast(
    airport_code: str, hours: int = Query(48, ge=1, le=168), db: Session = Depends(get_db)
):
    """
    Get hourly weather forecast for an airport.

    Args:
        airport_code: IATA airport code
        hours: Number of hours to forecast (1-168)
    """
    try:
        forecast_data = weather_client.get_hourly_forecast(airport_code, hours)

        return {
            "airport_code": airport_code.upper(),
            "forecast_hours": len(forecast_data),
            "generated_at": datetime.now().isoformat(),
            "forecasts": forecast_data,
        }

    except Exception as e:
        error_msg = f"Weather API error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/weather/aviation-briefing/{airport_code}")
def get_aviation_briefing(airport_code: str):
    """
    Get comprehensive aviation weather briefing.

    Args:
        airport_code: IATA airport code
    """
    try:
        briefing = weather_client.get_aviation_weather_briefing(airport_code)
        return briefing

    except Exception as e:
        error_msg = f"Weather API error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


# ========== FLIGHT TRACKING API ENDPOINTS ==========


@app.get("/flights/real-time")
def get_real_time_flights(
    flight_iata: Optional[str] = None,
    dep_iata: Optional[str] = None,
    arr_iata: Optional[str] = None,
    limit: int = Query(100, ge=1, le=100),
):
    """
    Get real-time flight information.

    Args:
        flight_iata: Flight IATA code (e.g., EK230)
        dep_iata: Departure airport IATA code
        arr_iata: Arrival airport IATA code
        limit: Maximum number of results (1-100)
    """
    try:
        flights = aviation_client.get_real_time_flights(
            flight_iata=flight_iata,
            dep_iata=dep_iata,
            arr_iata=arr_iata,
            limit=limit,
        )

        return {
            "query": {
                "flight_iata": flight_iata,
                "dep_iata": dep_iata,
                "arr_iata": arr_iata,
            },
            "count": len(flights),
            "flights": flights,
        }

    except Exception as e:
        error_msg = f"Flight tracking error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/flights/historical")
def get_historical_flights(
    flight_date: str,
    flight_iata: Optional[str] = None,
    dep_iata: Optional[str] = None,
    arr_iata: Optional[str] = None,
):
    """
    Get historical flight information for a specific date.

    Args:
        flight_date: Flight date in YYYY-MM-DD format
        flight_iata: Flight IATA code
        dep_iata: Departure airport IATA code
        arr_iata: Arrival airport IATA code
    """
    try:
        flights = aviation_client.get_historical_flights(
            flight_date=flight_date,
            flight_iata=flight_iata,
            dep_iata=dep_iata,
            arr_iata=arr_iata,
        )

        return {
            "query": {
                "date": flight_date,
                "flight_iata": flight_iata,
                "dep_iata": dep_iata,
                "arr_iata": arr_iata,
            },
            "count": len(flights),
            "flights": flights,
        }

    except Exception as e:
        error_msg = f"Flight tracking error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/flights/route-statistics")
def get_route_statistics(
    dep_iata: str,
    arr_iata: str,
    days_back: int = Query(30, ge=1, le=90),
):
    """
    Get historical statistics for a flight route.

    Args:
        dep_iata: Departure airport IATA code
        arr_iata: Arrival airport IATA code
        days_back: Number of days to analyze (1-90)
    """
    try:
        route_history = aviation_client.get_flight_route_history(
            dep_iata=dep_iata, arr_iata=arr_iata, days_back=days_back
        )

        if not route_history:
            return {
                "route": f"{dep_iata} → {arr_iata}",
                "error": "No historical data found for this route",
            }

        statistics = aviation_client.calculate_route_statistics(route_history)

        return {
            "route": f"{dep_iata} → {arr_iata}",
            "analysis_period": f"Last {days_back} days",
            "flights_analyzed": len(route_history),
            "statistics": statistics,
            "sample_flights": route_history[:5],  # First 5 flights as samples
        }

    except Exception as e:
        error_msg = f"Flight tracking error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


@app.get("/flights/airport-info/{airport_code}")
def get_airport_info(airport_code: str):
    """Get detailed airport information."""
    try:
        airport_info = aviation_client.get_airport_info(airport_code)
        return airport_info

    except Exception as e:
        error_msg = f"Flight tracking error: {str(e)}"
        raise HTTPException(status_code=500, detail=error_msg)


# ========== ENHANCED PREDICTION ENDPOINTS ==========


@app.post("/predict/enhanced")
def enhanced_prediction(
    flight_iata: str,
    dep_iata: str,
    arr_iata: str,
    scheduled_departure: str,  # ISO format datetime
    db: Session = Depends(get_db),
    background_tasks: BackgroundTasks = None,
):
    """
    Enhanced flight delay prediction using real-time weather and historical data.

    Args:
        flight_iata: Flight number (e.g., EK230)
        dep_iata: Departure airport code
        arr_iata: Arrival airport code
        scheduled_departure: Scheduled departure time (ISO format)
    """
    try:
        departure_time = datetime.fromisoformat(scheduled_departure)

        # Get current weather at departure airport
        dep_weather = weather_client.get_current_weather(dep_iata)

        # Get weather forecast at scheduled departure time
        forecast_weather = weather_client.get_weather_at_time(dep_iata, departure_time)

        # Get arrival weather
        arr_weather = weather_client.get_current_weather(arr_iata)

        # Get route statistics
        route_history = aviation_client.get_flight_route_history(dep_iata, arr_iata)
        route_stats = (
            aviation_client.calculate_route_statistics(route_history)
            if route_history
            else None
        )

        # Build features for ML model
        features = {
            "wind": forecast_weather.get("wind_speed_kts", 0),
            "visibility": forecast_weather.get("visibility_km", 10),
            "temperature": forecast_weather.get("temperature_c", 15),
            "precipitation": forecast_weather.get("precipitation_mm", 0),
            "route_delay_history": (
                route_stats["statistics"]["avg_delay_minutes"]
                if route_stats
                else 0
            ),
            "route_delay_percentage": (
                route_stats["statistics"]["delay_percentage"]
                if route_stats
                else 0
            ),
        }

        # Run prediction
        prob, delay = predict_delay(features)
        shap_values = explain_prediction(features)
        explanation = generate_explanation(shap_values)

        # Store prediction in database
        prediction = Prediction(
            flight_number=flight_iata,
            departure_airport=dep_iata,
            arrival_airport=arr_iata,
            scheduled_departure_time=departure_time,
            predicted_delay_minutes=delay,
            delay_probability=prob,
            model_version="v2.0-enhanced",
            features_used=features,
        )
        db.add(prediction)

        # Store SHAP explanation
        for feature, value in shap_values.items():
            shap_exp = ShapExplanation(
                prediction=prediction,
                feature_name=feature,
                shap_value=value,
            )
            db.add(shap_exp)

        db.commit()
        db.refresh(prediction)

        return {
            "flight_id": flight_iata,
            "route": f"{dep_iata} → {arr_iata}",
            "scheduled_departure": scheduled_departure,
            "delay_probability": round(prob, 3),
            "predicted_delay_minutes": round(delay, 2),
            "risk_level": (
                "HIGH" if prob > 0.7 else "MODERATE" if prob > 0.4 else "LOW"
            ),
            "weather_conditions": {
                "departure": dep_weather,
                "arrival": arr_weather,
                "forecast_at_departure": forecast_weather,
            },
            "route_statistics": route_stats,
            "shap_values": shap_values,
            "explanation": explanation,
            "prediction_id": prediction.id,
        }

    except Exception as e:
        # Handle both MCP and legacy API errors
        if "External API error" not in str(e):
            error_msg = f"External API error: {str(e)}"
        else:
            error_msg = str(e)
        raise HTTPException(status_code=500, detail=error_msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")


# ========== ALERTS AND ANALYTICS ==========


@app.get("/alerts/active")
def get_active_alerts(db: Session = Depends(get_db)):
    """Get all active high-risk alerts."""
    alerts = (
        db.query(Alert)
        .filter(Alert.alert_status == "ACTIVE")
        .order_by(Alert.created_at.desc())
        .limit(50)
        .all()
    )

    return {"count": len(alerts), "alerts": alerts}


@app.get("/analytics/predictions/recent")
def get_recent_predictions(
    limit: int = Query(50, ge=1, le=100), db: Session = Depends(get_db)
):
    """Get recent predictions with accuracy tracking."""
    predictions = (
        db.query(Prediction)
        .order_by(Prediction.prediction_timestamp.desc())
        .limit(limit)
        .all()
    )

    return {"count": len(predictions), "predictions": predictions}


@app.get("/analytics/accuracy")
def get_model_accuracy(days: int = Query(7, ge=1, le=90), db: Session = Depends(get_db)):
    """Get model accuracy metrics for the past N days."""
    cutoff_date = datetime.now() - timedelta(days=days)

    predictions = (
        db.query(Prediction)
        .filter(
            Prediction.prediction_timestamp >= cutoff_date,
            Prediction.actual_delay_minutes.isnot(None),
        )
        .all()
    )

    if not predictions:
        return {"error": "No validated predictions found for the specified period"}

    total = len(predictions)
    correct_predictions = sum(
        1
        for p in predictions
        if abs(p.predicted_delay_minutes - p.actual_delay_minutes) <= 15
    )

    accuracy = (correct_predictions / total) * 100

    return {
        "analysis_period_days": days,
        "total_predictions": total,
        "validated_predictions": total,
        "accuracy_percentage": round(accuracy, 2),
        "correct_within_15_minutes": correct_predictions,
    }


# ========== LOCATION AND GEOCODING ENDPOINTS ==========


@app.get("/location/airport/{airport_code}")
def get_airport_location_data(
    airport_code: str,
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive airport location data with timezone information.
    Requires Google Maps API key.
    
    Args:
        airport_code: IATA airport code (e.g., DXB, LHR, JFK)
        force_refresh: Force refresh from Google Maps API
    """
    if USE_MCP_CLIENTS and googlemaps_client:
        # Use MCP Google Maps client if available
        if not googlemaps_client.is_enabled():
            raise HTTPException(
                status_code=503,
                detail="Google Maps service not available (API key required)"
            )
        
        try:
            location_data = googlemaps_client.get_airport_location(
                airport_code,
                db_session=db,
                force_refresh=force_refresh
            )
            
            if not location_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Airport {airport_code} not found"
                )
            
            return {
                "airport_code": airport_code.upper(),
                "location": location_data,
                "from_cache": not force_refresh,
                "source": "GoogleMaps_MCP"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Location service error: {str(e)}"
            )
    else:
        # Fallback to legacy location service
        from services.location_service import LocationService
        
        try:
            location_service = LocationService(db)
            location_data = location_service.get_airport_location(
                airport_code,
                force_refresh=force_refresh
            )
            
            if not location_data:
                raise HTTPException(
                    status_code=404,
                    detail=f"Airport {airport_code} not found"
                )
            
            return {
                "airport_code": airport_code.upper(),
                "location": location_data,
                "from_cache": not force_refresh,
                "source": "GoogleMaps_Direct"
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Location service error: {str(e)}"
            )


@app.get("/location/route-distance")
def get_route_distance_data(
    origin: str = Query(..., description="Origin airport code"),
    destination: str = Query(..., description="Destination airport code"),
    force_refresh: bool = Query(False),
    db: Session = Depends(get_db)
):
    """
    Get distance and estimated duration between two airports.
    
    Args:
        origin: Origin airport IATA code
        destination: Destination airport IATA code
        force_refresh: Force refresh from Google Maps API
    """
    from services.location_service import LocationService
    from external_apis import GoogleMapsError
    
    try:
        location_service = LocationService(db)
        distance_data = location_service.get_route_distance(
            origin,
            destination,
            force_refresh=force_refresh
        )
        
        if not distance_data:
            raise HTTPException(
                status_code=404,
                detail=f"Route {origin} -> {destination} not found"
            )
        
        return {
            "route": f"{origin.upper()} → {destination.upper()}",
            "distance": distance_data,
            "from_cache": not force_refresh
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except GoogleMapsError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Location service error: {str(e)}"
        )


@app.get("/location/nearby-airports")
def get_nearby_airports_data(
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    radius_km: float = Query(100, ge=1, le=500),
    db: Session = Depends(get_db)
):
    """
    Find airports within radius of coordinates.
    
    Args:
        latitude: Center latitude (-90 to 90)
        longitude: Center longitude (-180 to 180)
        radius_km: Search radius in kilometers (1-500)
    """
    from services.location_service import LocationService
    
    try:
        location_service = LocationService(db)
        nearby_airports = location_service.get_nearby_airports(
            latitude,
            longitude,
            radius_km
        )
        
        return {
            "center": {
                "latitude": latitude,
                "longitude": longitude
            },
            "radius_km": radius_km,
            "airports_found": len(nearby_airports),
            "airports": nearby_airports
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Location search error: {str(e)}"
        )


@app.post("/location/geocode")
def geocode_address_endpoint(
    address: str = Query(..., min_length=3, max_length=500),
    db: Session = Depends(get_db)
):
    """
    Geocode an address to geographic coordinates.
    
    Args:
        address: Address string to geocode
    """
    from services.location_service import LocationService
    from external_apis import GoogleMapsError
    
    try:
        location_service = LocationService(db)
        geocode_result = location_service.geocode_and_cache(address)
        
        if not geocode_result:
            raise HTTPException(
                status_code=404,
                detail=f"Address not found: {address}"
            )
        
        return {
            "query": address,
            "result": geocode_result
        }
        
    except GoogleMapsError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Geocoding error: {str(e)}"
        )


@app.get("/location/validate-airport")
def validate_airport_coordinates_endpoint(
    airport_code: str = Query(..., min_length=3, max_length=4),
    latitude: float = Query(..., ge=-90, le=90),
    longitude: float = Query(..., ge=-180, le=180),
    tolerance_km: float = Query(50, ge=1, le=200),
    db: Session = Depends(get_db)
):
    """
    Validate if coordinates match expected airport location.
    
    Args:
        airport_code: IATA airport code
        latitude: Latitude to validate
        longitude: Longitude to validate
        tolerance_km: Tolerance in kilometers
    """
    from services.location_service import LocationService
    
    try:
        location_service = LocationService(db)
        is_valid = location_service.validate_airport_coordinates(
            airport_code,
            latitude,
            longitude,
            tolerance_km
        )
        
        return {
            "airport_code": airport_code.upper(),
            "provided_coordinates": {
                "latitude": latitude,
                "longitude": longitude
            },
            "tolerance_km": tolerance_km,
            "is_valid": is_valid
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Validation error: {str(e)}"
        )
