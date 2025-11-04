# Google Maps Integration - API Documentation

## 🗺️ Location and Geocoding Endpoints

### Security Notes
- All endpoints require valid `GOOGLE_MAPS_API_KEY` environment variable
- Rate limiting enforced: 50 requests/minute (configurable)
- Intelligent caching reduces API costs
- Input validation on all parameters

---

## GET `/location/airport/{airport_code}`

**Description**: Get comprehensive airport location data including coordinates, timezone, and address.

**Parameters**:
- `airport_code` (path, required): IATA airport code (3-4 characters)
- `force_refresh` (query, optional): Force refresh from Google Maps API (default: false)

**Caching**: Results cached for 90 days in database

**Example Request**:
```bash
curl http://localhost:8000/location/airport/DXB
```

**Example Response**:
```json
{
  "airport_code": "DXB",
  "location": {
    "airport_code": "DXB",
    "airport_name": "DXB Airport",
    "city": "Dubai",
    "country": "United Arab Emirates",
    "latitude": 25.2532,
    "longitude": 55.3657,
    "formatted_address": "Dubai International Airport - Dubai - United Arab Emirates",
    "place_id": "ChIJX8rPBVZxXz4RLhMrU5KYHRU",
    "timezone_id": "Asia/Dubai",
    "timezone_name": "Gulf Standard Time",
    "utc_offset_seconds": 14400,
    "elevation_meters": null,
    "last_verified": "2024-11-04T10:30:00"
  },
  "from_cache": true
}
```

**Use Cases**:
- Verify airport coordinates before weather API calls
- Display airport timezone for scheduling
- Validate user-entered airport codes

---

## GET `/location/route-distance`

**Description**: Calculate distance and estimated flight duration between two airports.

**Query Parameters**:
- `origin` (required): Origin airport IATA code
- `destination` (required): Destination airport IATA code
- `force_refresh` (optional): Force recalculation (default: false)

**Caching**: Results cached for 90 days in database

**Example Request**:
```bash
curl "http://localhost:8000/location/route-distance?origin=DXB&destination=LHR"
```

**Example Response**:
```json
{
  "route": "DXB → LHR",
  "distance": {
    "origin": "DXB",
    "destination": "LHR",
    "distance_meters": 5476000,
    "distance_km": 5476.0,
    "distance_nm": 2956.8,
    "great_circle_km": 5476.2,
    "estimated_flight_duration_minutes": 411,
    "last_calculated": "2024-11-04T10:30:00"
  },
  "from_cache": true
}
```

**Use Cases**:
- Calculate flight time for delay predictions
- Validate reasonable flight durations
- Route optimization analysis

---

## GET `/location/nearby-airports`

**Description**: Find all airports within specified radius of coordinates.

**Query Parameters**:
- `latitude` (required): Center latitude (-90 to 90)
- `longitude` (required): Center longitude (-180 to 180)
- `radius_km` (optional): Search radius in km (1-500, default: 100)

**Example Request**:
```bash
curl "http://localhost:8000/location/nearby-airports?latitude=25.2532&longitude=55.3657&radius_km=150"
```

**Example Response**:
```json
{
  "center": {
    "latitude": 25.2532,
    "longitude": 55.3657
  },
  "radius_km": 150,
  "airports_found": 3,
  "airports": [
    {
      "airport_code": "DXB",
      "airport_name": "Dubai International Airport",
      "city": "Dubai",
      "country": "United Arab Emirates",
      "latitude": 25.2532,
      "longitude": 55.3657,
      "distance_km": 0.0
    },
    {
      "airport_code": "SHJ",
      "airport_name": "Sharjah International Airport",
      "city": "Sharjah",
      "country": "United Arab Emirates",
      "latitude": 25.3286,
      "longitude": 55.5172,
      "distance_km": 18.4
    }
  ]
}
```

**Use Cases**:
- Find alternative airports for diversions
- Regional airport analysis
- Proximity-based recommendations

---

## POST `/location/geocode`

**Description**: Convert address string to geographic coordinates.

**Query Parameters**:
- `address` (required): Address to geocode (3-500 characters)

**Caching**: Results cached for 30 days in database

**Example Request**:
```bash
curl -X POST "http://localhost:8000/location/geocode?address=Dubai%20International%20Airport"
```

**Example Response**:
```json
{
  "query": "Dubai International Airport",
  "result": {
    "latitude": 25.2532,
    "longitude": 55.3657,
    "formatted_address": "Dubai International Airport - Dubai - United Arab Emirates",
    "place_id": "ChIJX8rPBVZxXz4RLhMrU5KYHRU",
    "from_cache": false
  }
}
```

**Use Cases**:
- Geocode user-entered addresses
- Validate location data
- Convert airport names to coordinates

---

## GET `/location/validate-airport`

**Description**: Validate if coordinates match expected airport location within tolerance.

**Query Parameters**:
- `airport_code` (required): IATA airport code (3-4 characters)
- `latitude` (required): Latitude to validate (-90 to 90)
- `longitude` (required): Longitude to validate (-180 to 180)
- `tolerance_km` (optional): Tolerance in km (1-200, default: 50)

**Example Request**:
```bash
curl "http://localhost:8000/location/validate-airport?airport_code=DXB&latitude=25.25&longitude=55.36&tolerance_km=10"
```

**Example Response**:
```json
{
  "airport_code": "DXB",
  "provided_coordinates": {
    "latitude": 25.25,
    "longitude": 55.36
  },
  "tolerance_km": 10,
  "is_valid": true
}
```

**Use Cases**:
- Validate user-entered coordinates
- Quality check for flight tracking data
- Detect coordinate errors

---

## 💰 Cost Management

### API Call Optimization

**Intelligent Caching**:
- Airport locations: 90-day cache
- Route distances: 90-day cache
- General geocoding: 30-day cache
- Cache hit tracking for monitoring

**Rate Limiting**:
- Default: 50 requests/minute
- Configurable via `GOOGLE_MAPS_RATE_LIMIT_PER_MINUTE`
- Automatic throttling when limit reached

**Cost Estimates** (Google Maps Platform):
- Geocoding: $5 per 1,000 requests
- Distance Matrix: $5 per 1,000 requests
- Places API: $17 per 1,000 requests
- Timezone: $5 per 1,000 requests

**With Caching**:
- First request: API call made
- Subsequent requests (within TTL): Database lookup (free)
- Average cost reduction: **90-95%**

---

## 🔒 Security Features

### API Key Protection
```python
# ✅ CORRECT - Key from environment
GOOGLE_MAPS_API_KEY=your_api_key_here

# ❌ WRONG - Never hardcode keys
api_key = "AIzaSyABCDEF123456789"
```

### Input Validation
- Latitude: -90 to 90
- Longitude: -180 to 180
- Airport codes: 3-4 alphanumeric characters
- Radius: 1-500 km
- Address length: 3-500 characters

### Error Handling
```json
{
  "detail": "Location service error: Rate limit exceeded"
}
```

**HTTP Status Codes**:
- `200`: Success
- `400`: Invalid input parameters
- `404`: Location/airport not found
- `429`: Rate limit exceeded
- `500`: Google Maps API error

---

## 🧪 Testing Examples

### Complete Location Workflow

```bash
# 1. Get airport location
curl http://localhost:8000/location/airport/JFK

# 2. Calculate route distance
curl "http://localhost:8000/location/route-distance?origin=JFK&destination=LHR"

# 3. Find nearby airports
curl "http://localhost:8000/location/nearby-airports?latitude=40.6413&longitude=-73.7781&radius_km=100"

# 4. Geocode address
curl -X POST "http://localhost:8000/location/geocode?address=John%20F%20Kennedy%20International%20Airport"

# 5. Validate coordinates
curl "http://localhost:8000/location/validate-airport?airport_code=JFK&latitude=40.64&longitude=-73.78&tolerance_km=5"
```

### Integration with Prediction

```python
# Enhanced prediction with location data
import requests

# Get route distance
distance_response = requests.get(
    "http://localhost:8000/location/route-distance",
    params={"origin": "DXB", "destination": "LHR"}
)
distance_data = distance_response.json()

# Get airport timezones
origin_tz = requests.get("http://localhost:8000/location/airport/DXB").json()
dest_tz = requests.get("http://localhost:8000/location/airport/LHR").json()

# Use in prediction
prediction = requests.post(
    "http://localhost:8000/predict/enhanced",
    json={
        "flight_iata": "EK230",
        "dep_iata": "DXB",
        "arr_iata": "LHR",
        "scheduled_departure": "2024-11-05T14:30:00",
        "route_distance_km": distance_data["distance"]["distance_km"],
        "origin_timezone": origin_tz["location"]["timezone_id"],
        "destination_timezone": dest_tz["location"]["timezone_id"]
    }
)
```

---

## 📊 Database Schema

### Tables Created

**airport_locations**:
- Primary cache for airport geocoding
- Includes timezone and elevation data
- 90-day verification cycle

**route_distances**:
- Cached distance calculations
- Both great-circle and actual distances
- Estimated flight duration

**geocoding_cache**:
- General address geocoding cache
- 30-day expiration
- Hit count tracking

### Views Available

**v_verified_airport_locations**:
```sql
SELECT * FROM v_verified_airport_locations 
WHERE days_since_verification < 30;
```

**v_route_analysis**:
```sql
SELECT * FROM v_route_analysis 
WHERE origin_airport = 'DXB' AND destination_airport = 'LHR';
```

---

## 🎯 Best Practices

### 1. Always Use Caching
```python
# First call - hits Google Maps API
location1 = requests.get("/location/airport/DXB")

# Second call - uses database cache
location2 = requests.get("/location/airport/DXB")

# Force refresh only when needed
location3 = requests.get("/location/airport/DXB?force_refresh=true")
```

### 2. Batch Operations
```python
# Instead of N separate calls
for airport in airports:
    get_location(airport)  # ❌ Many API calls

# Do this
locations = [get_location(airport) for airport in airports]  # ✅ Cached after first fetch
```

### 3. Monitor Cache Performance
```sql
-- Check cache hit rate
SELECT 
    airport_code,
    last_verified,
    EXTRACT(EPOCH FROM (NOW() - last_verified)) / 86400 AS days_old
FROM airport_locations
ORDER BY days_old DESC;
```

### 4. Handle Errors Gracefully
```python
try:
    location = get_airport_location("XYZ")
except HTTPException as e:
    if e.status_code == 404:
        # Airport not found - use fallback
        location = get_fallback_location("XYZ")
    else:
        # Other error - retry or alert
        raise
```

---

## 🚀 Performance Optimization

### Cache Warming
```python
# Warm cache for common airports
common_airports = ["DXB", "LHR", "JFK", "LAX", "SIN", "CDG", "FRA"]
for airport in common_airports:
    get_airport_location(airport)
```

### Periodic Verification
```python
# Verify old cache entries (run daily)
from datetime import datetime, timedelta

old_entries = session.query(AirportLocation).filter(
    AirportLocation.last_verified < datetime.now() - timedelta(days=80)
).all()

for entry in old_entries:
    # Refresh in background
    get_airport_location(entry.airport_code, force_refresh=True)
```

---

## 📈 Monitoring

### Key Metrics

```sql
-- Total cached airports
SELECT COUNT(*) FROM airport_locations;

-- Cache age distribution
SELECT 
    CASE 
        WHEN EXTRACT(EPOCH FROM (NOW() - last_verified)) / 86400 < 30 THEN 'Fresh (< 30 days)'
        WHEN EXTRACT(EPOCH FROM (NOW() - last_verified)) / 86400 < 60 THEN 'Good (30-60 days)'
        ELSE 'Stale (> 60 days)'
    END AS cache_status,
    COUNT(*) AS count
FROM airport_locations
GROUP BY cache_status;

-- Most used geocoding queries
SELECT search_query, cache_hits 
FROM geocoding_cache 
ORDER BY cache_hits DESC 
LIMIT 10;

-- API usage tracking
SELECT api_service, COUNT(*), AVG(response_time_ms)
FROM api_usage_logs
WHERE api_service = 'GOOGLE_MAPS'
  AND request_timestamp > NOW() - INTERVAL '24 hours'
GROUP BY api_service;
```

---

## 🔧 Configuration

### Environment Variables

```bash
# Required
GOOGLE_MAPS_API_KEY=your_api_key_here

# Optional - Feature toggles
GOOGLE_MAPS_GEOCODING_ENABLED=true
GOOGLE_MAPS_DISTANCE_MATRIX_ENABLED=true
GOOGLE_MAPS_PLACES_ENABLED=true

# Optional - Rate limiting
GOOGLE_MAPS_RATE_LIMIT_PER_MINUTE=50

# Optional - Cache TTL
GOOGLE_MAPS_CACHE_TTL_SECONDS=7776000  # 90 days
```

### Production Recommendations

1. **Restrict API Key**:
   - By IP address
   - By API (only enable needed APIs)
   - Set usage quotas

2. **Monitor Costs**:
   - Set up billing alerts
   - Track cache hit rate
   - Review usage reports

3. **Database Indexes**:
   - Already created in schema
   - Monitor query performance
   - Add custom indexes if needed

4. **Backup Strategy**:
   - Export cached location data
   - Periodic snapshots
   - Geographic redundancy

---

**Security Note**: This implementation follows production best practices with no hardcoded credentials, comprehensive input validation, rate limiting, and intelligent caching to minimize costs.
