# PreFlight AI - API Endpoints Documentation

## Base URL
```
http://localhost:8000
```

---

## 📋 Health & Status

### GET `/`
**Description**: Root endpoint with service status

**Response**:
```json
{
  "message": "PreFlight AI backend running",
  "version": "2.0",
  "services": {
    "database": "connected",
    "weather_api": "Open-Meteo",
    "flight_api": "AviationStack"
  }
}
```

### GET `/health`
**Description**: Comprehensive health check for all services

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2024-01-15T10:30:00",
  "services": {
    "database": true,
    "redis": true,
    "weather_api": true,
    "flight_api": true
  }
}
```

---

## 🌤️ Weather API Endpoints

### GET `/weather/current/{airport_code}`
**Description**: Get current weather conditions for an airport

**Parameters**:
- `airport_code` (path): IATA airport code (e.g., DXB, LHR, JFK)

**Example Request**:
```bash
curl http://localhost:8000/weather/current/DXB
```

**Response**:
```json
{
  "airport_code": "DXB",
  "timestamp": "2024-01-15T10:30:00",
  "temperature_c": 28.5,
  "wind_speed_kts": 12.5,
  "wind_direction_deg": 270,
  "wind_gust_kts": 18.2,
  "visibility_km": 10.0,
  "cloud_coverage_percent": 25,
  "precipitation_type": "NONE",
  "precipitation_mm": 0.0,
  "pressure_mb": 1013.2,
  "humidity_percent": 55,
  "data_source": "OPEN_METEO"
}
```

### GET `/weather/forecast/{airport_code}`
**Description**: Get hourly weather forecast for an airport

**Parameters**:
- `airport_code` (path): IATA airport code
- `hours` (query, optional): Number of hours to forecast (1-168, default: 48)

**Example Request**:
```bash
curl "http://localhost:8000/weather/forecast/LHR?hours=24"
```

**Response**:
```json
{
  "airport_code": "LHR",
  "forecast_hours": 24,
  "generated_at": "2024-01-15T10:30:00",
  "forecasts": [
    {
      "airport_code": "LHR",
      "timestamp": "2024-01-15T11:00:00",
      "temperature_c": 12.3,
      "wind_speed_kts": 15.8,
      "wind_direction_deg": 240,
      "visibility_km": 8.5,
      "cloud_coverage_percent": 60,
      "precipitation_type": "RAIN",
      "precipitation_mm": 0.5,
      "precipitation_probability": 45,
      "pressure_mb": 1015.0,
      "humidity_percent": 78
    }
    // ... more hourly forecasts
  ]
}
```

### GET `/weather/aviation-briefing/{airport_code}`
**Description**: Get comprehensive aviation weather briefing with operational concerns

**Parameters**:
- `airport_code` (path): IATA airport code

**Example Request**:
```bash
curl http://localhost:8000/weather/aviation-briefing/JFK
```

**Response**:
```json
{
  "airport_code": "JFK",
  "briefing_time": "2024-01-15T10:30:00",
  "current_conditions": {
    "temperature_c": -2.5,
    "wind_speed_kts": 28.5,
    "visibility_km": 3.2
  },
  "forecast_6h": [...],
  "forecast_24h_summary": {
    "avg_wind_speed": 22.3,
    "max_wind_speed": 35.6,
    "min_visibility": 2.8,
    "total_precipitation": 5.2
  },
  "operational_concerns": [
    "HIGH_WINDS",
    "LOW_VISIBILITY",
    "PRECIPITATION_EXPECTED"
  ],
  "risk_level": "HIGH"
}
```

---

## ✈️ Flight Tracking API Endpoints

### GET `/flights/real-time`
**Description**: Get real-time flight information

**Query Parameters**:
- `flight_iata` (optional): Flight IATA code (e.g., EK230)
- `dep_iata` (optional): Departure airport IATA code
- `arr_iata` (optional): Arrival airport IATA code
- `limit` (optional): Maximum results (1-100, default: 100)

**Example Requests**:
```bash
# Get specific flight
curl "http://localhost:8000/flights/real-time?flight_iata=EK230"

# Get all flights from DXB
curl "http://localhost:8000/flights/real-time?dep_iata=DXB&limit=50"

# Get all flights from DXB to LHR
curl "http://localhost:8000/flights/real-time?dep_iata=DXB&arr_iata=LHR"
```

**Response**:
```json
{
  "query": {
    "flight_iata": "EK230",
    "dep_iata": null,
    "arr_iata": null
  },
  "count": 1,
  "flights": [
    {
      "flight_iata": "EK230",
      "flight_number": "230",
      "airline_iata": "EK",
      "airline_name": "Emirates",
      "departure_airport": "DXB",
      "arrival_airport": "LHR",
      "scheduled_departure": "2024-01-15T14:30:00",
      "actual_departure": "2024-01-15T14:45:00",
      "scheduled_arrival": "2024-01-15T18:45:00",
      "estimated_arrival": "2024-01-15T19:00:00",
      "flight_status": "active",
      "delay_minutes": 15
    }
  ]
}
```

### GET `/flights/historical`
**Description**: Get historical flight information for a specific date

**Query Parameters**:
- `flight_date` (required): Flight date in YYYY-MM-DD format
- `flight_iata` (optional): Flight IATA code
- `dep_iata` (optional): Departure airport IATA code
- `arr_iata` (optional): Arrival airport IATA code

**Example Requests**:
```bash
# Get specific flight on a date
curl "http://localhost:8000/flights/historical?flight_date=2024-01-10&flight_iata=EK230"

# Get all flights on a route on a date
curl "http://localhost:8000/flights/historical?flight_date=2024-01-10&dep_iata=DXB&arr_iata=LHR"
```

**Response**:
```json
{
  "query": {
    "date": "2024-01-10",
    "flight_iata": "EK230",
    "dep_iata": null,
    "arr_iata": null
  },
  "count": 1,
  "flights": [
    {
      "flight_iata": "EK230",
      "departure_airport": "DXB",
      "arrival_airport": "LHR",
      "scheduled_departure": "2024-01-10T14:30:00",
      "actual_departure": "2024-01-10T14:52:00",
      "scheduled_arrival": "2024-01-10T18:45:00",
      "actual_arrival": "2024-01-10T19:12:00",
      "flight_status": "landed",
      "delay_minutes": 22
    }
  ]
}
```

### GET `/flights/route-statistics`
**Description**: Get historical statistics and delay patterns for a flight route

**Query Parameters**:
- `dep_iata` (required): Departure airport IATA code
- `arr_iata` (required): Arrival airport IATA code
- `days_back` (optional): Number of days to analyze (1-90, default: 30)

**Example Request**:
```bash
curl "http://localhost:8000/flights/route-statistics?dep_iata=DXB&arr_iata=LHR&days_back=30"
```

**Response**:
```json
{
  "route": "DXB → LHR",
  "analysis_period": "Last 30 days",
  "flights_analyzed": 58,
  "statistics": {
    "total_flights": 58,
    "delayed_flights": 12,
    "on_time_flights": 46,
    "avg_delay_minutes": 8.5,
    "max_delay_minutes": 45,
    "on_time_percentage": 79.3,
    "delay_percentage": 20.7
  },
  "sample_flights": [
    {
      "flight_date": "2024-01-14",
      "flight_iata": "EK230",
      "delay_minutes": 15
    }
    // ... 4 more samples
  ]
}
```

### GET `/flights/airport-info/{airport_code}`
**Description**: Get detailed airport information

**Parameters**:
- `airport_code` (path): IATA airport code

**Example Request**:
```bash
curl http://localhost:8000/flights/airport-info/DXB
```

**Response**:
```json
{
  "airport_iata": "DXB",
  "airport_name": "Dubai International Airport",
  "city": "Dubai",
  "country": "United Arab Emirates",
  "timezone": "Asia/Dubai",
  "latitude": 25.2532,
  "longitude": 55.3657
}
```

---

## 🎯 Enhanced Prediction Endpoints

### POST `/predict/enhanced`
**Description**: Enhanced flight delay prediction using real-time weather and historical route data

**Request Body**:
```json
{
  "flight_iata": "EK230",
  "dep_iata": "DXB",
  "arr_iata": "LHR",
  "scheduled_departure": "2024-01-20T14:30:00"
}
```

**Example Request**:
```bash
curl -X POST "http://localhost:8000/predict/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_iata": "EK230",
    "dep_iata": "DXB",
    "arr_iata": "LHR",
    "scheduled_departure": "2024-01-20T14:30:00"
  }'
```

**Response**:
```json
{
  "flight_id": "EK230",
  "route": "DXB → LHR",
  "scheduled_departure": "2024-01-20T14:30:00",
  "delay_probability": 0.342,
  "predicted_delay_minutes": 12.5,
  "risk_level": "LOW",
  "weather_conditions": {
    "departure": {
      "temperature_c": 28.5,
      "wind_speed_kts": 12.5,
      "visibility_km": 10.0,
      "precipitation_mm": 0.0
    },
    "arrival": {
      "temperature_c": 8.2,
      "wind_speed_kts": 18.3,
      "visibility_km": 7.5,
      "precipitation_mm": 0.5
    },
    "forecast_at_departure": {
      "temperature_c": 27.8,
      "wind_speed_kts": 14.2,
      "visibility_km": 9.5
    }
  },
  "route_statistics": {
    "total_flights": 58,
    "avg_delay_minutes": 8.5,
    "on_time_percentage": 79.3,
    "delay_percentage": 20.7
  },
  "shap_values": {
    "wind": 0.15,
    "visibility": -0.08,
    "route_delay_history": 0.12,
    "precipitation": 0.03
  },
  "explanation": "The flight has a low delay risk. The primary contributing factors are moderate historical route delays (12% impact) and current wind conditions (15% impact). Good visibility at both airports helps reduce delay risk.",
  "prediction_id": 1234
}
```

### POST `/score` (Legacy)
**Description**: Original scoring endpoint (kept for backward compatibility)

**Request Body**:
```json
{
  "flight_id": "EK230",
  "weather": {
    "wind_kts": 15,
    "visibility_km": 8
  },
  "atc": ["DELAY_15", "REROUTE"]
}
```

---

## 🚨 Alerts & Analytics

### GET `/alerts/active`
**Description**: Get all active high-risk flight alerts

**Example Request**:
```bash
curl http://localhost:8000/alerts/active
```

**Response**:
```json
{
  "count": 3,
  "alerts": [
    {
      "id": 1,
      "flight_number": "EK230",
      "departure_airport": "DXB",
      "arrival_airport": "LHR",
      "alert_type": "HIGH_DELAY_RISK",
      "severity": "HIGH",
      "delay_probability": 0.85,
      "predicted_delay_minutes": 45,
      "alert_status": "ACTIVE",
      "created_at": "2024-01-15T10:30:00",
      "notification_sent": true
    }
    // ... more alerts
  ]
}
```

### GET `/analytics/predictions/recent`
**Description**: Get recent predictions with accuracy tracking

**Query Parameters**:
- `limit` (optional): Number of predictions to return (1-100, default: 50)

**Example Request**:
```bash
curl "http://localhost:8000/analytics/predictions/recent?limit=20"
```

**Response**:
```json
{
  "count": 20,
  "predictions": [
    {
      "id": 1234,
      "flight_number": "EK230",
      "departure_airport": "DXB",
      "arrival_airport": "LHR",
      "scheduled_departure_time": "2024-01-15T14:30:00",
      "predicted_delay_minutes": 12.5,
      "actual_delay_minutes": 15.0,
      "delay_probability": 0.342,
      "prediction_timestamp": "2024-01-15T10:30:00",
      "model_version": "v2.0-enhanced"
    }
    // ... more predictions
  ]
}
```

### GET `/analytics/accuracy`
**Description**: Get model accuracy metrics for the past N days

**Query Parameters**:
- `days` (optional): Number of days to analyze (1-90, default: 7)

**Example Request**:
```bash
curl "http://localhost:8000/analytics/accuracy?days=30"
```

**Response**:
```json
{
  "analysis_period_days": 30,
  "total_predictions": 150,
  "validated_predictions": 150,
  "accuracy_percentage": 83.5,
  "correct_within_15_minutes": 125
}
```

### GET `/insights` (Legacy)
**Description**: Get AI-generated insights (legacy endpoint)

**Example Request**:
```bash
curl http://localhost:8000/insights
```

---

## 📊 Response Codes

| Code | Description |
|------|-------------|
| 200  | Success |
| 400  | Bad Request - Invalid parameters |
| 404  | Not Found - Resource doesn't exist |
| 500  | Internal Server Error - API/Database issue |
| 503  | Service Unavailable - External API down |

---

## 🔑 Error Response Format

```json
{
  "detail": "Weather API error: Airport coordinates not found for XYZ"
}
```

---

## 📝 Notes

### Supported Airports
The following airports have weather data available:
- DXB (Dubai)
- LHR (London Heathrow)
- JFK (New York JFK)
- LAX (Los Angeles)
- SIN (Singapore)
- FRA (Frankfurt)
- NRT (Tokyo Narita)
- DEL (New Delhi)
- CDG (Paris Charles de Gaulle)
- AMS (Amsterdam)
- HKG (Hong Kong)
- SYD (Sydney)
- ORD (Chicago O'Hare)
- ATL (Atlanta)
- DFW (Dallas/Fort Worth)

To add more airports, update `AIRPORT_COORDINATES` in `backend/external_apis/openmeteo_weather.py`.

### Rate Limits
- **Open-Meteo**: Unlimited (free tier)
- **AviationStack**: 100 calls/month (free tier)

### Data Freshness
- **Current Weather**: Real-time (updated every hour)
- **Weather Forecast**: 7-day forecast, hourly resolution
- **Flight Data**: Real-time for active flights, historical for past flights
- **Route Statistics**: Based on last 30-90 days of flight data

### Prediction Improvements
The prediction model gets more accurate as the flight date approaches:
- **7+ days out**: Uses only historical route statistics
- **3-7 days**: Adds weather forecast trends
- **0-3 days**: Uses real-time weather + recent route performance
- **Same day**: Maximum accuracy with current conditions

---

## 🧪 Testing Examples

### Complete Prediction Workflow
```bash
# 1. Check health
curl http://localhost:8000/health

# 2. Get current weather
curl http://localhost:8000/weather/current/DXB

# 3. Get route statistics
curl "http://localhost:8000/flights/route-statistics?dep_iata=DXB&arr_iata=LHR"

# 4. Run enhanced prediction
curl -X POST "http://localhost:8000/predict/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_iata": "EK230",
    "dep_iata": "DXB",
    "arr_iata": "LHR",
    "scheduled_departure": "2024-01-20T14:30:00"
  }'

# 5. Check active alerts
curl http://localhost:8000/alerts/active

# 6. View prediction accuracy
curl "http://localhost:8000/analytics/accuracy?days=7"
```
