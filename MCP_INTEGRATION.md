# MCP Integration Guide

## Overview

PreFlight AI now uses **Model Context Protocol (MCP)** servers for external data access, providing a standardized interface for weather data, flight tracking, and geocoding services.

## Architecture

### MCP Client Pattern

```
PreFlight AI Backend
    ↓
MCP Clients (with health checks)
    ↓
MCP Servers (HTTP endpoints)
    ↓
External APIs (Open-Meteo, AviationStack, Google Maps)
```

### Fallback Strategy

All MCP clients implement graceful fallback:
1. **Primary**: Connect to MCP server via HTTP
2. **Health Check**: Test `/health` endpoint on initialization
3. **Fallback**: If MCP server unavailable, use direct API calls
4. **Error Handling**: Comprehensive error handling and logging

## MCP Servers

### 1. Open-Meteo MCP Server (Weather Data)

**Source**: Open-source MCP server from Model Context Protocol project

**Repository**: https://github.com/modelcontextprotocol/servers/tree/main/src/weather

**Default URL**: `http://localhost:3000`

**Configuration**:
```env
OPENMETEO_MCP_SERVER_URL=http://localhost:3000
```

**MCP Tools**:
- `get_forecast` - Get weather forecast for location
- `get_current_weather` - Get current weather conditions

**Features**:
- ✅ Free, unlimited access
- ✅ No API key required
- ✅ Supports 15 major airports (DXB, LHR, JFK, LAX, etc.)
- ✅ Hourly forecasts up to 7 days
- ✅ Aviation-specific weather parameters

**Setup**:
```bash
# Clone MCP servers repository
git clone https://github.com/modelcontextprotocol/servers.git
cd servers/src/weather

# Install dependencies
npm install

# Run MCP server
npm start
```

**Docker Setup**:
```yaml
openmeteo-mcp:
  image: node:18-alpine
  volumes:
    - ./mcp-servers/weather:/app
  working_dir: /app
  command: npm start
  ports:
    - "3000:3000"
  environment:
    - PORT=3000
```

### 2. AviationStack MCP Server (Flight Tracking)

**Source**: Custom MCP adapter for AviationStack API

**Default URL**: `http://localhost:3001`

**Configuration**:
```env
AVIATIONSTACK_MCP_SERVER_URL=http://localhost:3001
AVIATIONSTACK_API_KEY=your_api_key_here  # For fallback
```

**MCP Tools**:
- `get_real_time_flights` - Get live flight data
- `get_historical_flights` - Get historical flight records
- `get_airport_info` - Get airport information

**Features**:
- ✅ Real-time flight tracking
- ✅ 30-90 day historical data
- ✅ Route statistics calculation
- ✅ Delay analysis
- ✅ Automatic delay calculation

**Setup**:

Create `mcp-servers/aviationstack/server.js`:

```javascript
const express = require('express');
const axios = require('axios');
const app = express();

app.use(express.json());

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'healthy' });
});

// MCP tool call endpoint
app.post('/call-tool', async (req, res) => {
    const { name, arguments: args } = req.body;
    
    try {
        const apiKey = process.env.AVIATIONSTACK_API_KEY;
        const baseUrl = 'https://api.aviationstack.com/v1';
        
        if (name === 'get_real_time_flights') {
            const response = await axios.get(`${baseUrl}/flights`, {
                params: {
                    access_key: apiKey,
                    ...args
                }
            });
            res.json({ result: response.data });
        }
        // ... other tools
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = process.env.PORT || 3001;
app.listen(PORT, () => {
    console.log(`AviationStack MCP Server running on port ${PORT}`);
});
```

**Docker Setup**:
```yaml
aviationstack-mcp:
  build: ./mcp-servers/aviationstack
  ports:
    - "3001:3001"
  environment:
    - PORT=3001
    - AVIATIONSTACK_API_KEY=${AVIATIONSTACK_API_KEY}
```

### 3. Google Maps MCP Client (Geocoding - Optional)

**Source**: Custom wrapper around Google Maps API

**Configuration**:
```env
GOOGLE_MAPS_API_KEY=your_google_maps_api_key_here  # Optional
```

**Features**:
- ✅ **Optional** - Only enabled if API key provided
- ✅ Airport location with timezone
- ✅ Route distance calculation
- ✅ Address geocoding
- ✅ Nearby airports search
- ✅ Coordinate validation

**Graceful Degradation**:
If no API key is provided, Google Maps features are disabled and endpoints return appropriate messages.

## MCP Client Usage

### Python Backend

```python
from mcp_clients import (
    OpenMeteoMCPClient,
    AviationStackMCPClient,
    GoogleMapsMCPClient
)
from mcp_clients.mcp_config import MCPConfig

# Initialize MCP clients
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

# Check if clients are using MCP servers
print(f"Weather using MCP: {weather_client.use_mcp}")
print(f"Aviation using MCP: {aviation_client.use_mcp}")
print(f"Google Maps enabled: {googlemaps_client.is_enabled()}")

# Use the clients
weather = weather_client.get_current_weather("DXB")
flights = aviation_client.get_real_time_flights(dep_iata="DXB", arr_iata="LHR")
location = googlemaps_client.get_airport_location("DXB", db_session=db)
```

### Health Checks

All MCP clients automatically test connectivity on initialization:

```python
# Weather client health check
if weather_client.use_mcp:
    print("✓ Connected to Open-Meteo MCP server")
else:
    print("⚠ Fallback to direct Open-Meteo API")

# Aviation client health check
if aviation_client.use_mcp:
    print("✓ Connected to AviationStack MCP server")
else:
    print("⚠ Fallback to direct AviationStack API")
```

## Environment Variables

Create `.env` file:

```env
# Database
DATABASE_URL=postgresql://preflight:preflight@postgres:5432/preflight_ai
REDIS_URL=redis://redis:6379/0

# MCP Server URLs
OPENMETEO_MCP_SERVER_URL=http://openmeteo-mcp:3000
AVIATIONSTACK_MCP_SERVER_URL=http://aviationstack-mcp:3001

# API Keys (for fallback)
AVIATIONSTACK_API_KEY=your_aviationstack_key
GOOGLE_MAPS_API_KEY=your_google_maps_key  # Optional

# MCP Timeouts
MCP_CONNECTION_TIMEOUT=5
MCP_REQUEST_TIMEOUT=30
```

## API Endpoints

### Health Check

```bash
GET /health

Response:
{
    "status": "healthy",
    "timestamp": "2024-01-15T10:30:00",
    "architecture": "MCP-based",
    "services": {
        "db_postgresql": true,
        "db_redis": true,
        "mcp_openmeteo": true,
        "mcp_aviationstack": true,
        "mcp_googlemaps": false
    }
}
```

### Weather Endpoints

```bash
# Current weather
GET /weather/current/{airport_code}

# Hourly forecast
GET /weather/forecast/{airport_code}?hours=48

# Aviation briefing
GET /weather/aviation-briefing/{airport_code}
```

### Flight Tracking Endpoints

```bash
# Real-time flights
GET /flights/real-time?dep_iata=DXB&arr_iata=LHR&limit=10

# Historical flights
GET /flights/historical?flight_date=2024-01-15&dep_iata=DXB

# Route statistics
GET /flights/route-statistics?dep_iata=DXB&arr_iata=LHR&days_back=30

# Airport information
GET /flights/airport-info/{airport_code}
```

### Location Endpoints (Optional)

```bash
# Airport location
GET /location/airport/{airport_code}

# Route distance
GET /location/route-distance?origin=DXB&destination=LHR

# Nearby airports
GET /location/nearby-airports?latitude=25.2532&longitude=55.3657&radius_km=100
```

## Testing MCP Servers

### Test Open-Meteo MCP Server

```bash
# Health check
curl http://localhost:3000/health

# Call tool
curl -X POST http://localhost:3000/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_forecast",
    "arguments": {
      "latitude": 25.2532,
      "longitude": 55.3657,
      "forecast_days": 1
    }
  }'
```

### Test AviationStack MCP Server

```bash
# Health check
curl http://localhost:3001/health

# Call tool
curl -X POST http://localhost:3001/call-tool \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_real_time_flights",
    "arguments": {
      "dep_iata": "DXB",
      "arr_iata": "LHR",
      "limit": 10
    }
  }'
```

## Troubleshooting

### MCP Server Not Available

**Symptom**: Logs show "MCP server not available, using direct API"

**Solution**:
1. Check if MCP servers are running
2. Verify environment variable URLs
3. Check network connectivity
4. Review MCP server logs

### Fallback Always Active

**Symptom**: Always using direct API despite MCP server running

**Solutions**:
1. Check MCP server health endpoint manually
2. Verify correct port mapping in Docker
3. Check firewall rules
4. Review connection timeout settings

### Google Maps Not Working

**Symptom**: Location endpoints return "service not available"

**Solutions**:
1. Verify `GOOGLE_MAPS_API_KEY` is set
2. Check API key has proper permissions
3. Ensure billing is enabled on Google Cloud
4. This is **optional** - app works without it

## Performance

### MCP vs Direct API

| Metric | MCP Server | Direct API |
|--------|-----------|------------|
| Latency | ~50-100ms | ~200-500ms |
| Caching | Server-side | Client-side |
| Rate Limiting | Centralized | Per-client |
| Monitoring | Unified | Distributed |

### Caching Strategy

- **Database**: Airport locations, historical data
- **Redis**: Real-time flight status (5 min TTL)
- **MCP Server**: Weather forecasts (15 min cache)

## Security

### API Key Management

```python
# ✅ Good - Use environment variables
api_key = os.getenv("AVIATIONSTACK_API_KEY")

# ❌ Bad - Hardcoded keys
api_key = "abc123def456"
```

### MCP Server Authentication

Future enhancement - add JWT authentication:

```python
headers = {
    "Authorization": f"Bearer {mcp_auth_token}"
}
response = requests.post(mcp_url, headers=headers, json=payload)
```

## Monitoring

### Health Check Endpoints

```bash
# Backend health
curl http://localhost:8000/health

# MCP server health
curl http://localhost:3000/health
curl http://localhost:3001/health
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)

# MCP clients log:
# - Connection status
# - Fallback events
# - API call latency
# - Error details
```

## Future Enhancements

1. **MCP Server Discovery**: Automatic service discovery
2. **Load Balancing**: Multiple MCP server instances
3. **Circuit Breaker**: Automatic fallback on repeated failures
4. **Metrics**: Prometheus metrics for MCP calls
5. **Authentication**: JWT-based MCP server auth
6. **WebSocket Support**: Real-time updates via WebSocket

## References

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [MCP Servers Repository](https://github.com/modelcontextprotocol/servers)
- [Open-Meteo API Documentation](https://open-meteo.com/en/docs)
- [AviationStack API Documentation](https://aviationstack.com/documentation)
- [Google Maps Platform Documentation](https://developers.google.com/maps)
