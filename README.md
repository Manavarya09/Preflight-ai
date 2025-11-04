
# PreFlight AI

**Production-Ready Flight Delay Prediction System**

Enterprise-grade flight delay prediction platform with Model Context Protocol (MCP) integration, 
real-time weather and flight tracking, AI-powered explainability, and comprehensive security features.

## Architecture

- **Backend**: FastAPI with MCP clients, rate limiting, input validation
- **MCP Servers**: Open-Meteo (weather), AviationStack (flights)
- **AI Engine**: Langflow + Ollama (Mistral) for explainable predictions
- **Database**: PostgreSQL + Redis caching
- **Frontend**: React with real-time dashboard
- **Security**: CORS, rate limiting, security headers, input sanitization

## Key Features

- Real-time flight tracking via AviationStack MCP Server
- Live weather data via Open-Meteo MCP Server
- AI-powered predictions with SHAP explainability
- Model Context Protocol architecture with automatic fallback
- Production security: rate limiting, input validation, CORS, security headers
- Docker Compose orchestration for easy deployment
- PostgreSQL + Redis for persistence and caching
- Comprehensive health monitoring and error handling

## Project Structure

```
preflight-ai/
├── backend/                  # FastAPI + MCP + Security
│   ├── app/
│   │   ├── main.py          # API endpoints
│   │   ├── config.py        # Configuration validation
│   │   ├── middleware/      # Security & rate limiting
│   │   ├── models/          # ML predictor + SHAP
│   │   ├── schemas/         # Pydantic schemas
│   │   └── services/        # External API clients
│   └── langflow_flow/       # Langflow definitions
├── frontend/                 # React SPA
│   └── src/
│       ├── components/      # UI components
│       └── utils/api.js     # API client
├── docker-compose.yml        # Container orchestration
└── .env.example              # Environment template
```

## Prerequisites

- Docker Desktop (or Docker Engine + Docker Compose plugin)
- API Keys (configure in `.env`):
  - AviationStack API key (required for flight tracking)
  - Google Maps API key (required for geocoding)
  - Langflow URL and flow ID (for AI predictions)

**Security Requirements:**
- Never commit API keys to version control
- Use environment variables or secrets management in production
- Restrict CORS origins (no wildcards)
- Configure rate limiting appropriately for your load

## Quick Start

### 1. Configure Environment

Copy `.env.example` to `.env` and configure:

```env
# Required API Keys
AVIATIONSTACK_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here
LANGFLOW_URL=http://langflow:7860/api/v1/run/your_flow_id

# Security (PRODUCTION)
ALLOWED_ORIGINS=https://yourdomain.com
API_RATE_LIMIT_PER_MINUTE=60/minute
APP_ENV=production

# Database
DATABASE_URL=postgresql://preflight:preflight@postgres:5432/preflight_ai
REDIS_URL=redis://redis:6379/0
```

**SECURITY WARNING**: Never commit `.env` file to version control. In production, use secrets management (AWS Secrets Manager, Azure Key Vault, etc.).

### 2. Deploy

```bash
# Development
docker-compose up --build

# Production (detached)
docker-compose up -d --build
```

### 3. Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

### 4. Health Check

```

Expected response includes service status for PostgreSQL, Redis, and MCP servers.

## API Endpoints

### Core Endpoints

- `GET /health` - Health check (DB, Redis, MCP servers)
- `GET /docs` - Interactive API documentation

### Weather (MCP-Powered)

- `GET /weather/current/{airport_code}` - Current conditions
- `GET /weather/forecast/{airport_code}` - Hourly forecast (7 days)
- `GET /weather/aviation-briefing/{airport_code}` - Aviation briefing

### Flights (MCP-Powered)

- `GET /flights/real-time` - Live flight data with filters
- `GET /flights/historical` - Historical records
- `GET /flights/route-statistics` - Route delay statistics
- `GET /flights/airport-info/{code}` - Airport information

### Predictions

- `POST /predict/enhanced` - Delay prediction with SHAP explainability
- `POST /score` - Score single flight
- `GET /insights` - AI-generated insights (Langflow)

### Location (Google Maps)

- `GET /location/airport/{code}` - Airport coordinates and timezone
- `GET /location/route-distance` - Distance between airports
- `GET /location/nearby-airports` - Airports within radius

**Rate Limits**: All endpoints are rate-limited per IP address. Configure `API_RATE_LIMIT_PER_MINUTE` in `.env`.

**Example:**

```

## Model Context Protocol (MCP)

PreFlight AI uses MCP servers for standardized data access:

```
Frontend → Backend (FastAPI) → MCP Clients → MCP Servers → External APIs
```

**MCP Servers:**
- **Open-Meteo**: Weather data (free, no API key)
- **AviationStack**: Flight tracking (requires API key)
- **Google Maps**: Geocoding (optional)

**Features:**
- Automatic fallback to direct API calls if MCP unavailable
- Health monitoring for all connections
- Intelligent caching at MCP server level

## Security Configuration

**Production Checklist:**

1. **Environment Variables**: Never commit `.env` file. Use secrets management.
2. **CORS**: Set `ALLOWED_ORIGINS` to specific domains (no wildcards).
3. **Rate Limiting**: Configure `API_RATE_LIMIT_PER_MINUTE` for your load.
4. **API Keys**: Restrict by IP address and API endpoints in provider dashboards.
5. **HTTPS**: Use reverse proxy (nginx, Traefik) with SSL certificates.
6. **Resource Limits**: Adjust Docker resource limits in `docker-compose.yml`.
7. **Monitoring**: Implement health checks and alerting.

**Validation**: Configuration validates on startup. Application fails fast in production if validation fails.

## Langflow Integration

Configure Langflow flow for AI-generated insights:
1. Access Langflow at http://localhost:7860
2. Create flow: `Input → Python (parse SHAP) → LLM (Ollama) → Output`
3. Configure Ollama node: `http://ollama:11434`
4. Update `LANGFLOW_URL` with flow ID

System maintains functionality with fallback messages if Langflow/Ollama unavailable.

## Production Deployment

**Before deploying to production:**

1. Review and configure all environment variables in `.env`
2. Enable HTTPS with reverse proxy
3. Configure monitoring and logging
4. Set up database backups
5. Test health endpoints
6. Verify rate limiting
7. Validate CORS configuration
8. Remove source code volume mount from `docker-compose.yml`

**Resource Requirements:**
- Backend: 0.5-2 CPU cores, 512MB-2GB RAM
- Frontend: Minimal (static build can be served separately)
- Database: Based on expected data volume
- Redis: Minimal (cache only)
