# 🚀 PreFlight AI - Quick Start Guide

Get your intelligent flight delay prediction system up and running in 10 minutes!

---

## ⚡ Prerequisites

- Docker & Docker Compose installed
- Python 3.10+ (for local development)
- Node.js 16+ (for frontend development)
- 4GB+ RAM available for Docker containers

---

## 🎯 Quick Start (Docker - Recommended)

### Step 1: Environment Setup

Create `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env
```

Edit `.env` with your API credentials:

```env
# PostgreSQL Database
POSTGRES_USER=preflight
POSTGRES_PASSWORD=your_secure_password_here
POSTGRES_DB=preflight_db
DATABASE_URL=postgresql://preflight:your_secure_password_here@postgres:5432/preflight_db

# Redis Cache
REDIS_URL=redis://redis:6379/0

# External APIs
AVIATIONSTACK_API_KEY=00a88306b41eda9c29cc2b29732c51e6
AVIATIONSTACK_BASE_URL=https://api.aviationstack.com/v1/

# Open-Meteo (No API key needed - it's free!)
OPENMETEO_BASE_URL=https://api.open-meteo.com/v1/forecast

# Notifications (Optional - leave blank if not using)
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token
TWILIO_FROM_NUMBER=+1234567890

SENDGRID_API_KEY=your_sendgrid_key
SENDGRID_FROM_EMAIL=alerts@preflightai.com

SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL

# Langflow
LANGFLOW_BASE_URL=http://langflow:7860

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
```

### Step 2: Start All Services

```bash
# Start core services (backend, frontend, database, redis, langflow, ollama)
docker-compose up -d

# Check status
docker-compose ps
```

Expected output:
```
NAME                 STATUS          PORTS
preflight-backend    Up 30 seconds   0.0.0.0:8000->8000/tcp
preflight-frontend   Up 30 seconds   0.0.0.0:3000->3000/tcp
preflight-postgres   Up 30 seconds   0.0.0.0:5432->5432/tcp
preflight-redis      Up 30 seconds   0.0.0.0:6379->6379/tcp
preflight-langflow   Up 30 seconds   0.0.0.0:7860->7860/tcp
preflight-ollama     Up 30 seconds   0.0.0.0:11434->11434/tcp
```

### Step 3: Initialize Database

```bash
# Run database migrations
docker-compose exec backend alembic upgrade head

# Or import the schema directly
docker-compose exec -T postgres psql -U preflight -d preflight_db < backend/database/schema.sql
```

### Step 4: Pull Ollama Model

```bash
# Download Mistral model for AI explanations
docker-compose exec ollama ollama pull mistral
```

### Step 5: Verify Everything Works

```bash
# Test API health
curl http://localhost:8000/health

# Expected response:
# {
#   "status": "healthy",
#   "services": {
#     "database": true,
#     "redis": true,
#     "weather_api": true,
#     "flight_api": true
#   }
# }
```

### Step 6: Test a Prediction

```bash
curl -X POST "http://localhost:8000/predict/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_iata": "EK230",
    "dep_iata": "DXB",
    "arr_iata": "LHR",
    "scheduled_departure": "2024-01-25T14:30:00"
  }'
```

---

## 🌐 Access Your Services

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | React dashboard |
| **Backend API** | http://localhost:8000 | FastAPI REST API |
| **API Docs** | http://localhost:8000/docs | Interactive Swagger UI |
| **Langflow** | http://localhost:7860 | AI workflow designer |
| **pgAdmin** | http://localhost:5050 | Database manager (with `--profile tools`) |
| **Redis Commander** | http://localhost:8081 | Redis browser (with `--profile tools`) |

### Start with Management Tools

```bash
# Include pgAdmin and Redis Commander
docker-compose --profile tools up -d
```

---

## 📊 Test the Complete Workflow

### 1. Get Current Weather
```bash
curl http://localhost:8000/weather/current/DXB
```

### 2. Get Route Statistics
```bash
curl "http://localhost:8000/flights/route-statistics?dep_iata=DXB&arr_iata=LHR&days_back=30"
```

### 3. Run Enhanced Prediction
```bash
curl -X POST "http://localhost:8000/predict/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_iata": "EK230",
    "dep_iata": "DXB",
    "arr_iata": "LHR",
    "scheduled_departure": "2024-01-25T14:30:00"
  }'
```

### 4. Check Active Alerts
```bash
curl http://localhost:8000/alerts/active
```

### 5. View Prediction Accuracy
```bash
curl "http://localhost:8000/analytics/accuracy?days=7"
```

---

## 🛠️ Development Mode

### Backend Development

```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

---

## 🔧 Troubleshooting

### Problem: Containers won't start

```bash
# Check logs
docker-compose logs backend
docker-compose logs postgres

# Restart services
docker-compose restart
```

### Problem: Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Test connection
docker-compose exec postgres psql -U preflight -d preflight_db -c "SELECT 1;"
```

### Problem: Ollama model not loading

```bash
# Check if model exists
docker-compose exec ollama ollama list

# Pull model again
docker-compose exec ollama ollama pull mistral

# Test model
docker-compose exec ollama ollama run mistral "Hello"
```

### Problem: API calls failing

```bash
# Check API keys in .env file
cat .env | grep API_KEY

# Test Open-Meteo (no key needed)
curl "https://api.open-meteo.com/v1/forecast?latitude=25.25&longitude=55.36&current=temperature_2m"

# Test AviationStack (with your key)
curl "https://api.aviationstack.com/v1/flights?access_key=00a88306b41eda9c29cc2b29732c51e6&limit=1"
```

### Problem: Port already in use

```bash
# Find process using port 8000
lsof -i :8000  # On macOS/Linux
netstat -ano | findstr :8000  # On Windows

# Change port in docker-compose.yml
# backend:
#   ports:
#     - "8001:8000"  # Use 8001 instead
```

---

## 📚 Next Steps

1. **Customize Airport List**: Add more airports in `backend/external_apis/openmeteo_weather.py`
2. **Configure Notifications**: Add Twilio/SendGrid/Slack credentials in `.env`
3. **Enhance Langflow Workflow**: Open http://localhost:7860 and modify the agent
4. **Integrate Frontend**: Update React dashboard to use new API endpoints
5. **Add Authentication**: Implement JWT tokens for production use

---

## 🧪 API Testing

### Using Swagger UI
1. Open http://localhost:8000/docs
2. Try out endpoints interactively
3. View request/response schemas

### Using Postman
1. Import collection from `backend/API_ENDPOINTS.md`
2. Set environment variables
3. Run test scenarios

### Using Python
```python
import requests

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Enhanced prediction
prediction = requests.post(
    'http://localhost:8000/predict/enhanced',
    json={
        'flight_iata': 'EK230',
        'dep_iata': 'DXB',
        'arr_iata': 'LHR',
        'scheduled_departure': '2024-01-25T14:30:00'
    }
)
print(prediction.json())
```

---

## 🎓 Learn More

- **API Documentation**: See `backend/API_ENDPOINTS.md` for all endpoints
- **Integration Guide**: See `INTEGRATION_GUIDE.md` for system architecture
- **Enhancement Plan**: See `ENHANCEMENT_PLAN.md` for future features
- **Database Schema**: See `backend/database/schema.sql` for data structure

---

## 💡 Pro Tips

1. **Use Redis Caching**: Weather and flight data are cached for 5-10 minutes
2. **Monitor API Usage**: Check `/analytics/accuracy` regularly
3. **Set Up Alerts**: Configure notifications for high-risk flights
4. **Validate Predictions**: Update `actual_delay_minutes` after flights land
5. **Backup Database**: Use `pg_dump` to backup PostgreSQL data

---

## 🚀 Production Deployment

### Using Docker Compose (Simple)

```bash
# Build production images
docker-compose -f docker-compose.yml -f docker-compose.prod.yml build

# Start with production config
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Using Kubernetes (Advanced)

```bash
# Coming soon: Kubernetes manifests
# - backend-deployment.yaml
# - postgres-statefulset.yaml
# - redis-deployment.yaml
# - ingress.yaml
```

---

## 📞 Support

- **Issues**: Check `TROUBLESHOOTING.md`
- **API Questions**: See `backend/API_ENDPOINTS.md`
- **Architecture**: See `INTEGRATION_GUIDE.md`
- **Database**: See `backend/database/schema.sql`

---

## ✅ Success Checklist

- [ ] All containers running (`docker-compose ps`)
- [ ] Database initialized (`SELECT COUNT(*) FROM predictions;`)
- [ ] Ollama model loaded (`ollama list`)
- [ ] Health check passing (`/health` returns 200)
- [ ] Weather API working (`/weather/current/DXB`)
- [ ] Flight API working (`/flights/real-time`)
- [ ] Prediction working (`/predict/enhanced`)
- [ ] Frontend accessible (http://localhost:3000)
- [ ] Langflow accessible (http://localhost:7860)

---

**🎉 Congratulations! Your PreFlight AI system is now running!**

Start making predictions and watch your system get smarter with every flight! ✈️
