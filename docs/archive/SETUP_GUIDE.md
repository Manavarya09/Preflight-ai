# 🚀 PreFlight AI - Complete Setup Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [API Keys Setup](#api-keys-setup)
4. [Database Initialization](#database-initialization)
5. [Langflow Configuration](#langflow-configuration)
6. [Testing the System](#testing-the-system)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **Docker Desktop** (Windows/Mac) or **Docker Engine + Docker Compose** (Linux)
- **Git** for cloning the repository
- **Text Editor** (VS Code recommended)

### Recommended System Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+ (16GB recommended for Ollama)
- **Storage**: 20GB+ free space
- **GPU**: Optional but recommended for Ollama (NVIDIA with CUDA support)

---

## ⚡ Quick Start

### Step 1: Clone the Repository
```bash
git clone https://github.com/Manavarya09/Preflight-ai.git
cd Preflight-ai
```

### Step 2: Create Environment File
```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your actual API keys (see next section)
notepad .env  # Windows
# or
nano .env     # Linux/Mac
```

### Step 3: Start All Services
```bash
# Start core services
docker-compose up -d

# To also start database tools (pgAdmin, Redis Commander)
docker-compose --profile tools up -d

# To include monitoring (Prometheus, Grafana)
docker-compose --profile monitoring up -d
```

### Step 4: Verify Services Are Running
```bash
# Check status of all containers
docker-compose ps

# Expected output: All services should show "Up" or "healthy"
```

### Step 5: Access the Applications
- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:5000
- **API Documentation**: http://localhost:5000/docs
- **Langflow**: http://localhost:7860
- **pgAdmin** (if enabled): http://localhost:5050
- **Redis Commander** (if enabled): http://localhost:8081

---

## 🔑 API Keys Setup

You need to sign up for the following services and get API keys:

### 1. OpenWeatherMap (Weather Data)
1. Go to https://openweathermap.org/api
2. Click "Sign Up" and create a free account
3. Navigate to "API keys" in your account
4. Copy your API key
5. Add to `.env`: `OPENWEATHER_API_KEY=your_key_here`

**Free Tier**: 1,000 calls/day, 60 calls/minute

### 2. AviationStack (Flight Tracking)
1. Go to https://aviationstack.com/
2. Sign up for a free account
3. Copy your API key from the dashboard
4. Add to `.env`: `AVIATIONSTACK_API_KEY=your_key_here`

**Free Tier**: 100 calls/month (sufficient for testing)

### 3. Twilio (SMS Notifications)
1. Go to https://www.twilio.com/try-twilio
2. Sign up and verify your phone number
3. Get your Account SID and Auth Token from the dashboard
4. Get a Twilio phone number
5. Add to `.env`:
   ```
   TWILIO_ACCOUNT_SID=your_sid_here
   TWILIO_AUTH_TOKEN=your_token_here
   TWILIO_PHONE_NUMBER=+1234567890
   ```

**Free Tier**: $15 trial credit (covers ~500 SMS)

### 4. SendGrid (Email Notifications)
1. Go to https://sendgrid.com/
2. Sign up for a free account
3. Create an API key: Settings → API Keys → Create API Key
4. Verify a sender email address
5. Add to `.env`:
   ```
   SENDGRID_API_KEY=your_key_here
   SENDGRID_FROM_EMAIL=your_verified_email@example.com
   ```

**Free Tier**: 100 emails/day forever

### 5. Slack (Team Notifications)
1. Go to https://api.slack.com/messaging/webhooks
2. Click "Create your Slack app"
3. Enable "Incoming Webhooks"
4. Add webhook to your desired channel
5. Copy the webhook URL
6. Add to `.env`: `SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/WEBHOOK/URL`

**Cost**: Free

---

## 🗄️ Database Initialization

### Automatic Initialization (Recommended)
The database schema is automatically created when you first start the services:

```bash
# Start PostgreSQL and wait for it to initialize
docker-compose up -d postgres

# Wait 30 seconds for initialization
# Check logs to confirm
docker-compose logs postgres
```

### Manual Database Setup
If you need to manually initialize or reset the database:

```bash
# Connect to PostgreSQL container
docker-compose exec postgres psql -U preflight -d preflight_db

# Run schema manually
\i /docker-entrypoint-initdb.d/01-schema.sql

# Verify tables were created
\dt

# Exit
\q
```

### Populate Sample Data (Optional)
```bash
# Run sample data script
docker-compose exec backend python scripts/seed_data.py
```

---

## 🎨 Langflow Configuration

### Step 1: Access Langflow
1. Open http://localhost:7860 in your browser
2. Wait for Langflow to fully load

### Step 2: Import Workflow
1. Click on "Import" or "Upload Flow"
2. Select `backend/langflow_flow/preflight_ai_flow_router.json`
3. The workflow will appear in the visual editor

### Step 3: Configure Ollama Connection
1. Find the LLM nodes (Ollama_HighRisk_Model and Ollama_LowRisk_Model)
2. Verify the Base URL is set to: `http://ollama:11434`
3. Verify the model is set to: `mistral`

### Step 4: Pull Mistral Model
```bash
# Pull the Mistral model into Ollama
docker-compose exec ollama ollama pull mistral

# Verify model is available
docker-compose exec ollama ollama list
```

### Step 5: Test the Workflow
1. Click "Run" in Langflow
2. Provide sample input:
   ```json
   {
     "delay_prob": 0.78,
     "crosswind": 0.23,
     "visibility": -0.12,
     "atc": 0.09
   }
   ```
3. Check the output for a natural language explanation

### Step 6: Get Flow ID
1. Look at the URL: `http://localhost:7860/flow/[FLOW_ID]`
2. Copy the FLOW_ID
3. Update `.env`: `LANGFLOW_FLOW_ID=your_flow_id_here`
4. Restart backend: `docker-compose restart backend`

---

## 🧪 Testing the System

### 1. Test Backend Health
```bash
curl http://localhost:5000/
# Expected: {"message":"PreFlight AI backend running"}
```

### 2. Test Database Connection
```bash
curl http://localhost:5000/health/database
# Expected: {"postgresql": {"connected": true}, "redis": {"connected": true}}
```

### 3. Test Weather API
```bash
curl http://localhost:5000/weather/DXB
# Expected: Weather data for Dubai airport
```

### 4. Test Flight Prediction
```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "TEST123",
    "scheduled_departure": "2025-11-05T10:00:00Z",
    "scheduled_arrival": "2025-11-05T14:00:00Z",
    "weather": {"wind_kts": 18, "visibility_km": 6},
    "gate": "A12",
    "atc": "ground hold"
  }'
```

### 5. Test Notification (Optional)
```bash
# Only if you configured Twilio
curl -X POST http://localhost:5000/notify/sms \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "TEST123",
    "delay_minutes": 25,
    "phone_number": "+1234567890"
  }'
```

---

## 🔍 Troubleshooting

### Container Won't Start
```bash
# View logs for specific service
docker-compose logs backend
docker-compose logs postgres
docker-compose logs langflow

# Restart a specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Database Connection Errors
```bash
# Check if PostgreSQL is ready
docker-compose exec postgres pg_isready -U preflight

# Reset database (WARNING: Deletes all data!)
docker-compose down -v
docker-compose up -d postgres
```

### Ollama Model Issues
```bash
# Check if Mistral is downloaded
docker-compose exec ollama ollama list

# If not, pull it
docker-compose exec ollama ollama pull mistral

# Test Ollama directly
docker-compose exec ollama ollama run mistral "Hello, test message"
```

### Langflow Not Connecting to Ollama
1. Verify Ollama is running: `docker-compose ps ollama`
2. Check Ollama logs: `docker-compose logs ollama`
3. In Langflow, ensure Base URL is `http://ollama:11434` (not localhost)
4. Restart Langflow: `docker-compose restart langflow`

### Port Already in Use
```bash
# On Windows
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# On Linux/Mac
lsof -i :5000
lsof -i :3000

# Kill the process or change ports in docker-compose.yml
```

### API Keys Not Working
1. Check `.env` file has no extra spaces or quotes
2. Restart backend after changing `.env`: `docker-compose restart backend`
3. Verify API keys are active in their respective dashboards
4. Check API usage limits aren't exceeded

### Out of Memory
```bash
# Increase Docker Desktop memory limit
# Settings → Resources → Memory → Increase to 8GB+

# Or reduce services
docker-compose up -d backend frontend postgres redis
# (Skip Ollama if you don't have enough RAM)
```

---

## 📊 Monitoring & Logs

### View Real-time Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f langflow

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Access Databases
```bash
# PostgreSQL (if pgAdmin enabled)
# Open http://localhost:5050
# Login: admin@preflight.ai / admin_secure_pass

# Redis (if Redis Commander enabled)
# Open http://localhost:8081

# Or use CLI
docker-compose exec postgres psql -U preflight -d preflight_db
docker-compose exec redis redis-cli
```

---

## 🔄 Updating the System

### Pull Latest Changes
```bash
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Update Dependencies
```bash
# Backend
docker-compose exec backend pip install -r requirements.txt

# Or rebuild
docker-compose build backend
docker-compose up -d backend
```

---

## 🛑 Stopping the System

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including data (WARNING!)
docker-compose down -v
```

---

## 📞 Support

If you encounter issues:

1. Check the [Troubleshooting](#troubleshooting) section
2. Search existing GitHub issues
3. Create a new issue with:
   - Error message
   - Output of `docker-compose ps`
   - Relevant logs from `docker-compose logs`

---

## 🎉 Success!

Once everything is running, you should be able to:
- ✅ Access the dashboard at http://localhost:3000
- ✅ See live flight predictions
- ✅ Receive real-time alerts
- ✅ View AI-generated explanations
- ✅ Query historical data
- ✅ Generate reports

**Welcome to PreFlight AI!** 🚀✈️
