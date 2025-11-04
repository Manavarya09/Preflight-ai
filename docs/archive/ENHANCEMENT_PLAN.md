# 🚀 PreFlight AI - Comprehensive Enhancement Plan

## 📋 Executive Summary

This document outlines a complete enhancement plan to transform PreFlight AI from a prediction system into a full-featured intelligent aviation operations platform with database persistence, external API integrations, and file system capabilities.

---

## 🎯 Enhancement Goals

1. **Historical Intelligence** - Learn from past predictions to improve accuracy
2. **Real-world Data** - Integrate live weather, flight tracking, and ATC data
3. **Actionable Alerts** - Automatically notify stakeholders via SMS/Email
4. **Compliance & Reporting** - Generate audit logs and management reports
5. **Scalability** - Handle thousands of flights with caching and optimization

---

## 📊 Phase 1: Database Integration

### PostgreSQL Schema Design

#### Tables Overview
```sql
-- Core Flight Operations
flights_history           → Historical flight records with actual outcomes
predictions              → All ML predictions with timestamps
alerts                   → System-generated alerts
alert_actions            → User responses to alerts
weather_snapshots        → Weather data at prediction time

-- Model Management
model_versions           → Track ML model versions and performance
model_metrics            → Accuracy, precision, recall per model version
shap_explanations        → Store SHAP values for analysis

-- User & System
user_preferences         → Notification settings, dashboard configs
audit_logs              → All system actions for compliance
api_usage_logs          → Track external API calls and costs
```

#### Key Relationships
```
flights_history (1) -----> (N) predictions
predictions (1) ---------> (N) alerts
alerts (1) -------------> (N) alert_actions
predictions (1) ---------> (1) shap_explanations
model_versions (1) ------> (N) predictions
```

### Redis Cache Strategy
```
Key Pattern                    | TTL    | Purpose
-------------------------------|--------|----------------------------------
flight:{id}:status            | 5 min  | Current flight status
flight:{id}:prediction        | 1 hour | Latest prediction cache
weather:{airport}:current     | 10 min | Current weather conditions
alerts:active                 | -      | Active alerts queue (Redis List)
ratelimit:{api}:{key}         | 1 hour | API rate limiting
session:{user_id}             | 24 hrs | User session data
```

---

## 🌐 Phase 2: External API Integrations

### A. Weather Data APIs

#### 1. OpenWeatherMap
**Endpoint:** `https://api.openweathermap.org/data/2.5/weather`
**Use Case:** Real-time weather at airports
**Data Retrieved:**
- Wind speed & direction
- Visibility
- Precipitation
- Temperature
- Cloud coverage

**Langflow Integration:**
```python
# New Langflow node: "Fetch_Live_Weather"
def get_weather(airport_code):
    response = requests.get(
        f"https://api.openweathermap.org/data/2.5/weather?q={airport_code}&appid={API_KEY}"
    )
    return {
        "wind_kts": response['wind']['speed'] * 1.94384,  # Convert m/s to knots
        "visibility_km": response['visibility'] / 1000,
        "conditions": response['weather'][0]['description']
    }
```

#### 2. Aviation Weather Center (NOAA)
**Endpoint:** `https://aviationweather.gov/api/data/metar`
**Use Case:** Official METAR reports for aviation
**Data Retrieved:**
- Decoded METAR strings
- Wind shear warnings
- Runway visual range

---

### B. Flight Tracking APIs

#### 3. AviationStack / FlightAware
**Endpoint:** `http://api.aviationstack.com/v1/flights`
**Use Case:** Real-time flight status and history
**Data Retrieved:**
- Actual departure/arrival times
- Current flight phase (taxi, airborne, landed)
- Aircraft type and registration
- Historical on-time performance

**Why This Matters:**
- Compare predictions vs actual outcomes
- Auto-validate model accuracy
- Trigger retraining when accuracy drops

**Langflow Node:**
```python
# "Validate_Prediction" node
def validate_prediction(flight_id, predicted_delay):
    # Get actual outcome from API
    actual = aviationstack_client.get_actual_delay(flight_id)
    
    # Store in database for accuracy tracking
    db.store_validation(flight_id, predicted_delay, actual)
    
    # If error > threshold, flag for model retraining
    if abs(predicted_delay - actual) > 15:  # 15 min threshold
        db.flag_for_retraining(flight_id)
```

---

### C. Notification APIs

#### 4. Twilio (SMS)
**Use Case:** Send SMS alerts to crew and passengers
**Endpoint:** `https://api.twilio.com/2010-04-01/Accounts/{AccountSid}/Messages.json`

**Langflow Node:**
```python
# "Notify_Crew_SMS" node
def send_crew_alert(flight_id, delay_minutes, crew_phone):
    message = f"""
    PREFLIGHT AI ALERT
    Flight: {flight_id}
    Predicted Delay: {delay_minutes} min
    Recommend early crew check-in.
    View details: https://preflight.ai/flights/{flight_id}
    """
    twilio_client.messages.create(
        to=crew_phone,
        from_=TWILIO_NUMBER,
        body=message
    )
```

#### 5. SendGrid (Email)
**Use Case:** Detailed reports to operations team
**Langflow Node:**
```python
# "Email_Operations_Report" node
def send_ops_report(flight_details, shap_values, explanation):
    html_content = generate_email_template(flight_details, shap_values, explanation)
    
    sendgrid_client.send(
        to="ops-team@airline.com",
        subject=f"High Risk Alert: {flight_details['id']}",
        html=html_content,
        attachments=[generate_pdf_report(flight_details)]
    )
```

#### 6. Slack Webhooks
**Use Case:** Real-time alerts to operations Slack channel
**Langflow Node:**
```python
# "Post_To_Slack" node
def post_slack_alert(flight_id, delay_prob, key_factors):
    slack_webhook.post({
        "text": f"🚨 High Risk Flight Detected",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Flight:* {flight_id}\n*Delay Probability:* {delay_prob}%\n*Top Factor:* {key_factors[0]}"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Dashboard"},
                        "url": f"https://preflight.ai/flights/{flight_id}"
                    }
                ]
            }
        ]
    })
```

---

### D. Airport & ATC APIs

#### 7. FAA SWIM (System Wide Information Management)
**Use Case:** Official ATC delays and airspace restrictions
**Data Retrieved:**
- Ground delay programs
- Ground stops
- Airspace flow programs
- TFR (Temporary Flight Restrictions)

**Integration Pattern:**
```python
# "Check_ATC_Programs" node
def check_atc_delays(origin, destination):
    swim_data = faa_swim_client.query({
        "airports": [origin, destination],
        "program_types": ["GDP", "GS", "AFP"]
    })
    
    return {
        "has_delays": len(swim_data['programs']) > 0,
        "programs": swim_data['programs'],
        "estimated_impact_minutes": calculate_impact(swim_data)
    }
```

---

## 📁 Phase 3: File System Operations

### A. Model Management

#### Model Versioning System
```python
# "Save_Model_Version" node
def save_model_version(model, version_number, metrics):
    filepath = f"/app_data/models/lstm_xgboost_v{version_number}.pkl"
    
    # Save model
    joblib.dump(model, filepath)
    
    # Save metadata
    metadata = {
        "version": version_number,
        "timestamp": datetime.now().isoformat(),
        "accuracy": metrics['accuracy'],
        "precision": metrics['precision'],
        "recall": metrics['recall'],
        "training_samples": metrics['training_samples']
    }
    
    with open(f"/app_data/models/metadata_v{version_number}.json", "w") as f:
        json.dump(metadata, f)
    
    # Store in database
    db.insert_model_version(metadata)
```

#### Auto Model Selection
```python
# "Load_Best_Model" node
def load_best_model():
    # Query database for best performing model
    best_version = db.query("""
        SELECT version_number 
        FROM model_versions 
        WHERE accuracy > 0.90 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    
    model_path = f"/app_data/models/lstm_xgboost_v{best_version}.pkl"
    return joblib.load(model_path)
```

---

### B. Report Generation

#### Daily Operations Report
```python
# "Generate_Daily_Report" node
def generate_daily_report(date):
    # Query database for day's data
    flights = db.get_flights_by_date(date)
    predictions = db.get_predictions_by_date(date)
    alerts = db.get_alerts_by_date(date)
    
    # Generate PDF
    pdf = PDFReport()
    pdf.add_title(f"PreFlight AI Daily Report - {date}")
    pdf.add_section("Summary", {
        "Total Flights": len(flights),
        "Predictions Made": len(predictions),
        "Alerts Triggered": len(alerts),
        "Average Delay": calculate_avg(predictions)
    })
    pdf.add_chart("Delay Distribution", create_histogram(predictions))
    pdf.add_chart("Accuracy Metrics", create_accuracy_chart(predictions))
    
    # Save to file system
    output_path = f"/app_data/reports/daily/report_{date}.pdf"
    pdf.save(output_path)
    
    # Also store in database
    db.store_report_metadata(date, output_path)
    
    return output_path
```

#### Incident Investigation Reports
```python
# "Generate_Incident_Report" node
def generate_incident_report(flight_id, incident_type):
    """
    When a flight has major delay or prediction failure,
    generate detailed analysis report
    """
    # Gather all related data
    flight = db.get_flight_complete_history(flight_id)
    predictions = db.get_all_predictions_for_flight(flight_id)
    weather = db.get_weather_snapshots(flight_id)
    shap_values = db.get_shap_explanations(flight_id)
    
    # Generate detailed PDF
    pdf = IncidentReport()
    pdf.add_flight_timeline(flight)
    pdf.add_prediction_analysis(predictions)
    pdf.add_shap_breakdown(shap_values)
    pdf.add_weather_correlation(weather)
    pdf.add_recommendations()
    
    output_path = f"/app_data/reports/incident/{flight_id}_{incident_type}.pdf"
    pdf.save(output_path)
    
    return output_path
```

---

### C. Data Export & Analysis

#### CSV Export for Data Science Teams
```python
# "Export_Training_Data" node
def export_training_data(start_date, end_date):
    """
    Export validated predictions for model retraining
    """
    query = """
        SELECT 
            f.flight_id,
            f.origin,
            f.destination,
            p.predicted_delay,
            p.actual_delay,
            p.delay_probability,
            w.wind_kts,
            w.visibility_km,
            w.precipitation,
            s.crosswind,
            s.visibility_impact,
            s.atc_impact
        FROM flights_history f
        JOIN predictions p ON f.flight_id = p.flight_id
        JOIN weather_snapshots w ON p.prediction_id = w.prediction_id
        JOIN shap_explanations s ON p.prediction_id = s.prediction_id
        WHERE f.date BETWEEN %s AND %s
        AND p.actual_delay IS NOT NULL
    """
    
    df = pd.read_sql(query, db_connection, params=[start_date, end_date])
    
    output_path = f"/app_data/exports/training_data_{start_date}_{end_date}.csv"
    df.to_csv(output_path, index=False)
    
    return output_path
```

---

## 🔄 Phase 4: Enhanced Langflow Workflow

### New Workflow Architecture

```
                        START (Flight Scored)
                               ↓
                    ┌──────────────────────┐
                    │  Fetch Live Weather  │ ← OpenWeatherMap API
                    │  (API Node)          │
                    └──────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Check ATC Delays    │ ← FAA SWIM API
                    │  (API Node)          │
                    └──────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Store in Database   │ ← PostgreSQL
                    │  (DB Node)           │
                    └──────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Cache Prediction    │ ← Redis
                    │  (Cache Node)        │
                    └──────────────────────┘
                               ↓
                    ┌──────────────────────┐
                    │  Router: Risk Level  │
                    │  (Logic Node)        │
                    └──────────────────────┘
                        ↙          ↘
                HIGH RISK          LOW RISK
                    ↓                  ↓
         ┌─────────────────┐   ┌──────────────┐
         │ Format Context  │   │ Format Data  │
         └─────────────────┘   └──────────────┘
                    ↓                  ↓
         ┌─────────────────┐   ┌──────────────┐
         │ Ollama LLM      │   │ Ollama LLM   │
         │ (High Risk)     │   │ (Low Risk)   │
         └─────────────────┘   └──────────────┘
                    ↓                  ↓
         ┌─────────────────┐   ┌──────────────┐
         │ Create Alert    │   │ Store Result │
         │ (DB Insert)     │   │ (DB Insert)  │
         └─────────────────┘   └──────────────┘
                    ↓
         ┌─────────────────┐
         │ Notify Crew     │ ← Twilio SMS
         │ (API Node)      │
         └─────────────────┘
                    ↓
         ┌─────────────────┐
         │ Email Ops Team  │ ← SendGrid
         │ (API Node)      │
         └─────────────────┘
                    ↓
         ┌─────────────────┐
         │ Post to Slack   │ ← Slack Webhook
         │ (API Node)      │
         └─────────────────┘
                    ↓
         ┌─────────────────┐
         │ Generate Report │ ← File System
         │ (File Node)     │
         └─────────────────┘
                    ↓
                  OUTPUT
```

---

## 🔧 Phase 5: Backend Service Updates

### New Backend Structure
```
backend/
├── app/
│   ├── main.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py          → PostgreSQL & Redis connections
│   │   ├── models.py               → SQLAlchemy models
│   │   └── crud.py                 → Database operations
│   ├── external_apis/
│   │   ├── __init__.py
│   │   ├── weather.py              → OpenWeatherMap client
│   │   ├── flight_tracking.py     → AviationStack client
│   │   ├── notifications.py       → Twilio, SendGrid, Slack
│   │   └── faa_swim.py            → FAA ATC data
│   ├── file_handlers/
│   │   ├── __init__.py
│   │   ├── model_manager.py       → Save/load ML models
│   │   ├── report_generator.py    → PDF report creation
│   │   └── data_exporter.py       → CSV exports
│   ├── models/                     → (existing)
│   ├── schemas/                    → (existing)
│   └── services/
│       ├── langflow_client.py     → (existing)
│       ├── cache_service.py       → Redis operations
│       └── validation_service.py  → Prediction validation
```

---

## 🐳 Phase 6: Docker Infrastructure

### Updated docker-compose.yml
```yaml
version: '3.8'

services:
  # Existing services
  backend:
    build: ./backend
    environment:
      - LANGFLOW_URL=http://langflow:7860/api/v1/predict/${FLOW_ID}
      - DATABASE_URL=postgresql://preflight:password@postgres:5432/preflight_db
      - REDIS_URL=redis://redis:6379/0
      - OPENWEATHER_API_KEY=${OPENWEATHER_API_KEY}
      - AVIATIONSTACK_API_KEY=${AVIATIONSTACK_API_KEY}
      - TWILIO_ACCOUNT_SID=${TWILIO_ACCOUNT_SID}
      - TWILIO_AUTH_TOKEN=${TWILIO_AUTH_TOKEN}
      - SENDGRID_API_KEY=${SENDGRID_API_KEY}
      - SLACK_WEBHOOK_URL=${SLACK_WEBHOOK_URL}
    volumes:
      - app_data:/app_data
    ports:
      - "5000:5000"
    depends_on:
      - postgres
      - redis
      - langflow
      - ollama

  frontend:
    build: ./frontend
    environment:
      - REACT_APP_API_URL=http://backend:5000
    ports:
      - "3000:3000"

  langflow:
    image: langflowai/langflow:latest
    environment:
      - DATABASE_URL=postgresql://preflight:password@postgres:5432/langflow_db
    ports:
      - "7860:7860"
    depends_on:
      - postgres

  ollama:
    image: ollama/ollama
    ports:
      - "11434:11434"
    volumes:
      - ollama_models:/root/.ollama

  # NEW SERVICES
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=preflight
      - POSTGRES_PASSWORD=password
      - POSTGRES_DB=preflight_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backend/database/init.sql:/docker-entrypoint-initdb.d/init.sql
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"

  pgadmin:
    image: dpage/pgadmin4
    environment:
      - PGADMIN_DEFAULT_EMAIL=admin@preflight.ai
      - PGADMIN_DEFAULT_PASSWORD=admin
    ports:
      - "5050:80"
    depends_on:
      - postgres

volumes:
  postgres_data:
  redis_data:
  ollama_models:
  app_data:
```

---

## 📅 Implementation Timeline

### Week 1: Database Foundation
- [ ] Design PostgreSQL schema
- [ ] Create SQLAlchemy models
- [ ] Set up migrations with Alembic
- [ ] Implement CRUD operations
- [ ] Add Redis caching layer

### Week 2: External APIs
- [ ] Integrate OpenWeatherMap
- [ ] Integrate AviationStack/FlightAware
- [ ] Set up Twilio for SMS
- [ ] Set up SendGrid for email
- [ ] Configure Slack webhooks

### Week 3: File Operations
- [ ] Implement model versioning system
- [ ] Create PDF report generator
- [ ] Build CSV export functionality
- [ ] Set up logging infrastructure

### Week 4: Langflow Enhancement
- [ ] Create new workflow with DB nodes
- [ ] Add API call nodes
- [ ] Implement file operation nodes
- [ ] Test end-to-end flow

### Week 5: Backend Integration
- [ ] Update FastAPI endpoints
- [ ] Add validation service
- [ ] Implement auto-retraining triggers
- [ ] Create admin dashboard

### Week 6: Testing & Optimization
- [ ] Load testing with 1000+ concurrent flights
- [ ] API cost optimization
- [ ] Cache hit rate optimization
- [ ] Security audit

---

## 💰 Cost Estimates

### API Costs (Monthly)
```
Service             | Free Tier          | Paid (1000 flights/day)
--------------------|--------------------|-----------------------
OpenWeatherMap      | 1000 calls/day     | $40/month (60k calls)
AviationStack       | 100 calls/month    | $50/month (10k calls)
Twilio (SMS)        | $15 credit         | $150/month (2000 SMS)
SendGrid (Email)    | 100 emails/day     | $15/month (40k emails)
Slack               | Free webhooks      | Free
FAA SWIM            | Free (gov service) | Free
--------------------|--------------------|-----------------------
TOTAL               | ~$15 trial budget  | ~$255/month production
```

### Infrastructure Costs
```
Resource         | Development        | Production
-----------------|--------------------|-----------------
PostgreSQL       | Docker (free)      | AWS RDS: $50/mo
Redis            | Docker (free)      | AWS ElastiCache: $30/mo
Storage          | 10GB local         | AWS S3: $5/mo
Ollama           | Local GPU/CPU      | Dedicated server: $100/mo
-----------------|--------------------|-----------------
TOTAL            | $0                 | ~$185/month
```

**TOTAL MONTHLY COST: ~$440 for production-grade system**

---

## 🎯 Success Metrics

After implementation, track these KPIs:

1. **Prediction Accuracy**
   - Target: >92% for delays >15 min
   - Measure: Compare predicted vs actual delays

2. **System Performance**
   - API response time: <500ms
   - Database query time: <100ms
   - Cache hit rate: >80%

3. **User Engagement**
   - Alerts acknowledged: >90%
   - Reports generated: Daily
   - Crew notifications sent: Real-time

4. **Cost Efficiency**
   - API calls per prediction: <3
   - Storage per flight: <5MB
   - Total monthly cost: <$500

---

## 🚀 Next Steps

Ready to implement? Here's what we'll create:

1. ✅ Database schema SQL files
2. ✅ SQLAlchemy models
3. ✅ API client wrappers
4. ✅ Enhanced Langflow workflow JSON
5. ✅ Updated docker-compose.yml
6. ✅ Environment configuration templates
7. ✅ Setup scripts and documentation

**Shall I proceed with creating all these files?**
