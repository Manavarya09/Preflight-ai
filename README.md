
# PreFlight AI

**Intelligent Flight Delay Prediction with Real-Time Weather & Flight Tracking**

PreFlight AI pairs a cinematic airline operations dashboard with a production-ready FastAPI backend,
**Model Context Protocol (MCP)** server integration, Langflow workflow automation, and an Ollama-powered LLM 
for explainable insights. The architecture leverages MCP servers for standardized access to weather data, 
flight tracking, and geocoding services with automatic fallback to direct APIs.

## 🚀 Key Features

- ✈️ **Real-Time Flight Tracking** via AviationStack MCP Server
- 🌤️ **Live Weather Data** via Open-Meteo MCP Server  
- 🗺️ **Airport Geocoding** via Google Maps (optional)
- 🤖 **AI-Powered Predictions** with Langflow + Ollama (Mistral)
- 📊 **SHAP Explainability** for transparent ML predictions
- 🔄 **MCP Architecture** with automatic fallback
- 🐳 **Full Docker Compose** stack for one-command deployment
- 📈 **PostgreSQL + Redis** for data persistence and caching

## 📁 Project Layout

```
preflight-ai/
├── backend/                  # FastAPI service + MCP clients
│   ├── app/
│   │   ├── main.py          # API endpoints (MCP-enabled)
│   │   ├── models/          # ML models & SHAP explainability
│   │   ├── schemas/         # Pydantic data models
│   │   └── services/        # Langflow + location services
│   ├── mcp_clients/         # 🆕 MCP client implementations
│   │   ├── openmeteo_mcp_client.py    # Weather MCP client
│   │   ├── aviationstack_mcp_client.py # Flight tracking MCP
│   │   ├── googlemaps_mcp_client.py   # Geocoding (optional)
│   │   └── mcp_config.py              # Centralized config
│   ├── database/            # PostgreSQL models & migrations
│   ├── external_apis/       # Legacy API clients (fallback)
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                 # React dashboard with animations
│   ├── src/
│   │   ├── components/      # UI components + Locomotive Scroll
│   │   └── utils/           # API client utilities
│   ├── public/
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml        # Full stack orchestration
├── MCP_INTEGRATION.md        # 🆕 MCP setup guide
└── README.md
```

## 📋 Prerequisites

- **Python 3.10+** (backend development)
- **Node.js 18+** (frontend development)
- **Docker Desktop** (or Docker Engine + Docker Compose plugin)
- **API Keys** (optional but recommended):
  - AviationStack API key (for flight tracking fallback)
  - Google Maps API key (for geocoding - fully optional)

## 🚀 Quick Start (Docker)

### 1. Configure Environment Variables

Create `.env` file in project root:

```env
# Database
DATABASE_URL=postgresql://preflight:preflight@postgres:5432/preflight_ai
REDIS_URL=redis://redis:6379/0

# MCP Server URLs (will be added to docker-compose)
OPENMETEO_MCP_SERVER_URL=http://openmeteo-mcp:3000
AVIATIONSTACK_MCP_SERVER_URL=http://aviationstack-mcp:3001

# API Keys (optional - enables fallback)
AVIATIONSTACK_API_KEY=your_aviationstack_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key  # Optional

# Langflow
LANGFLOW_URL=http://langflow:7860/api/v1/run/<FLOW_ID>
```

### 2. Start All Services

```bash
# Build and start all containers
docker-compose up --build

# Or run in detached mode
docker-compose up -d --build
```

### 3. Access Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | React dashboard |
| **Backend API** | http://localhost:8000 | FastAPI + MCP clients |
| **Langflow** | http://localhost:7860 | AI workflow builder |
| **Ollama** | http://localhost:11434 | Local LLM (Mistral) |
| **PostgreSQL** | localhost:5432 | Database |
| **Redis** | localhost:6379 | Cache |

### 4. Verify MCP Integration

```bash
# Check health status
curl http://localhost:8000/health

# Expected response includes MCP status:
{
  "status": "healthy",
  "architecture": "MCP-based",
  "services": {
    "db_postgresql": true,
    "db_redis": true,
    "mcp_openmeteo": true,
    "mcp_aviationstack": true,
    "mcp_googlemaps": false  // if no API key
  }
}
```

> **Note**: MCP servers provide standardized access to external APIs. If MCP servers are unavailable, 
> the system automatically falls back to direct API calls. See `MCP_INTEGRATION.md` for details.

## Local Development

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

Create a `.env` file in `frontend/` (or copy `.env.example`) to point the dashboard at the backend when running locally without Docker:

```
REACT_APP_API_URL=http://localhost:5000
```

## 📡 API Overview

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service health check with MCP status |
| `/health` | GET | Comprehensive health check (DB, Redis, MCP servers) |

### Weather Endpoints (MCP-Powered)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/weather/current/{airport_code}` | GET | Current weather conditions |
| `/weather/forecast/{airport_code}` | GET | Hourly forecast (up to 7 days) |
| `/weather/aviation-briefing/{airport_code}` | GET | Aviation weather briefing |

### Flight Tracking Endpoints (MCP-Powered)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/flights/real-time` | GET | Live flight data with filters |
| `/flights/historical` | GET | Historical flight records |
| `/flights/route-statistics` | GET | Route delay statistics (30-90 days) |
| `/flights/airport-info/{code}` | GET | Airport information |

### Prediction Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/predict/enhanced` | POST | Enhanced delay prediction with SHAP |
| `/score` | POST | Score single flight with explainability |
| `/insights` | GET | AI-generated insights via Langflow |

### Location Endpoints (Optional - Requires Google Maps API)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/location/airport/{code}` | GET | Airport location with timezone |
| `/location/route-distance` | GET | Distance between airports |
| `/location/nearby-airports` | GET | Find airports within radius |

**Example Request:**

```bash
# Get real-time flights from DXB to LHR
curl "http://localhost:8000/flights/real-time?dep_iata=DXB&arr_iata=LHR&limit=10"

# Get current weather at Dubai Airport
curl "http://localhost:8000/weather/current/DXB"

# Enhanced prediction with all data sources
curl -X POST "http://localhost:8000/predict/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_iata": "EK230",
    "dep_iata": "DXB",
    "arr_iata": "LHR",
    "scheduled_departure": "2024-01-20T14:30:00"
  }'
```

The frontend dashboard calls these endpoints through `frontend/src/utils/api.js` 
and renders live probabilities, SHAP factors, and LLM-generated explanations 
with graceful fallbacks when services are offline.

## 🔌 Model Context Protocol (MCP) Integration

PreFlight AI uses **MCP servers** for standardized access to external data sources:

### Architecture

```
Frontend → Backend (FastAPI)
              ↓
         MCP Clients (with health checks)
              ↓
         MCP Servers (HTTP endpoints)
              ↓
         External APIs (Open-Meteo, AviationStack, Google Maps)
```

### Benefits

- ✅ **Standardized Interface**: Consistent tool-based API across all data sources
- ✅ **Automatic Fallback**: Graceful degradation to direct APIs if MCP unavailable
- ✅ **Health Monitoring**: Real-time status of all MCP connections
- ✅ **Production Ready**: Comprehensive error handling and logging
- ✅ **Caching**: Intelligent caching at MCP server level

### MCP Servers Used

1. **Open-Meteo MCP Server** (Weather Data)
   - Source: https://github.com/modelcontextprotocol/servers/tree/main/src/weather
   - Free, unlimited access
   - No API key required
   
2. **AviationStack MCP Server** (Flight Tracking)
   - Custom MCP adapter for AviationStack API
   - Real-time + historical flight data
   - Requires API key for fallback
   
3. **Google Maps MCP Client** (Geocoding - Optional)
   - Custom wrapper around Google Maps API
   - Only enabled if API key provided
   - Graceful degradation if unavailable

**For detailed MCP setup instructions, see [`MCP_INTEGRATION.md`](./MCP_INTEGRATION.md)**

## 🤖 Langflow + Ollama

1. Run `langflow run` (if developing outside Docker) and open `http://localhost:7860`.
2. Build a flow: `Input → Python (parse SHAP) → LLM (Ollama) → Output`.
3. Configure the Ollama node to hit `http://ollama:11434` in Docker or
   `http://localhost:11434` when running locally.
4. Copy the Flow ID and update `LANGFLOW_URL` accordingly (either set the
   environment variable or change the default in `backend/app/services/langflow_client.py`).

With the flow configured, the backend will produce natural-language
explanations for each scored flight while still working even if Langflow/Ollama
are offline (fallback messages are returned).

## Testing

- Frontend: `npm test` inside `frontend/`
- Backend: add FastAPI tests under `backend/tests` (pytest recommended)

## Troubleshooting

- **CORS errors:** ensure `REACT_APP_API_URL` points at the FastAPI origin in the current environment.
- **Langflow timeouts:** the backend returns a readable fallback message so the dashboard stays usable even if Langflow or Ollama are down.
- **Docker build failures:** prune previous images or rebuild with `docker-compose build --no-cache`.

Happy flying! 🚀✈️
