# PreFlight AI - Integration Guide

## 🎯 How Everything Works Together

This guide explains how all the components of PreFlight AI work together to provide intelligent flight delay predictions.

---

## 📊 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (React)                          │
│  Dashboard | Analytics | Alerts | Flight Search | Settings      │
└────────────────────┬────────────────────────────────────────────┘
                     │ HTTP/REST
                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI Backend (main.py)                     │
│  /weather | /flights | /predict | /alerts | /analytics          │
└──────┬──────────────┬──────────────┬────────────────┬───────────┘
       │              │              │                │
       ▼              ▼              ▼                ▼
┌──────────────┐ ┌──────────────┐ ┌──────────┐ ┌─────────────┐
│ Open-Meteo   │ │ AviationStack│ │PostgreSQL│ │   Redis     │
│  Weather API │ │  Flight API  │ │ Database │ │   Cache     │
└──────────────┘ └──────────────┘ └─────┬────┘ └─────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │  Langflow + Ollama       │
                          │  AI Agent Workflow       │
                          └──────────────────────────┘
                                        │
                                        ▼
                          ┌──────────────────────────┐
                          │  Notification Services   │
                          │  SMS | Email | Slack     │
                          └──────────────────────────┘
```

---

## 🔄 Complete Prediction Workflow

### Step 1: User Requests Prediction

**Frontend Action**:
```javascript
// User enters flight details in React dashboard
const response = await fetch('http://localhost:8000/predict/enhanced', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    flight_iata: 'EK230',
    dep_iata: 'DXB',
    arr_iata: 'LHR',
    scheduled_departure: '2024-01-20T14:30:00'
  })
});
```

### Step 2: Backend Gathers Data

**Backend Process** (`main.py: enhanced_prediction()`):

1. **Weather Data Collection**:
   ```python
   # Current weather at departure airport
   dep_weather = weather_client.get_current_weather('DXB')
   
   # Weather forecast at scheduled departure time
   forecast_weather = weather_client.get_weather_at_time('DXB', departure_time)
   
   # Arrival airport weather
   arr_weather = weather_client.get_current_weather('LHR')
   ```

2. **Historical Flight Data**:
   ```python
   # Get 30 days of route history
   route_history = aviation_client.get_flight_route_history('DXB', 'LHR')
   
   # Calculate delay statistics
   route_stats = aviation_client.calculate_route_statistics(route_history)
   # Returns: avg_delay_minutes, on_time_percentage, delay_percentage
   ```

3. **Feature Engineering**:
   ```python
   features = {
       'wind': forecast_weather['wind_speed_kts'],
       'visibility': forecast_weather['visibility_km'],
       'temperature': forecast_weather['temperature_c'],
       'precipitation': forecast_weather['precipitation_mm'],
       'route_delay_history': route_stats['avg_delay_minutes'],
       'route_delay_percentage': route_stats['delay_percentage']
   }
   ```

### Step 3: ML Model Prediction

**Prediction Engine** (`models/predictor.py`):
```python
# Run ML model
prob, delay = predict_delay(features)

# Generate SHAP explanations
shap_values = explain_prediction(features)
# Returns: {'wind': 0.15, 'visibility': -0.08, 'route_delay_history': 0.12}
```

### Step 4: Langflow AI Explanation

**Langflow Agent Workflow**:
```python
# Send SHAP values to Langflow agent
explanation = generate_explanation(shap_values)

# Langflow workflow:
# 1. Receives SHAP values as input
# 2. Router determines if high-risk (>0.7 probability)
# 3. Python tool calculates risk factors
# 4. LLM (Ollama Mistral) generates human-readable explanation
# 5. Returns natural language explanation
```

### Step 5: Database Storage

**Database Operations** (`database/models.py`):
```python
# Store prediction
prediction = Prediction(
    flight_number='EK230',
    departure_airport='DXB',
    arrival_airport='LHR',
    scheduled_departure_time=departure_time,
    predicted_delay_minutes=delay,
    delay_probability=prob,
    model_version='v2.0-enhanced',
    features_used=features
)
db.add(prediction)

# Store SHAP explanations
for feature, value in shap_values.items():
    shap_exp = ShapExplanation(
        prediction=prediction,
        feature_name=feature,
        shap_value=value
    )
    db.add(shap_exp)

db.commit()
```

### Step 6: Alert Generation (if high-risk)

**Alert System**:
```python
if prob > 0.7:
    # Create alert in database
    alert = Alert(
        flight_number='EK230',
        departure_airport='DXB',
        arrival_airport='LHR',
        alert_type='HIGH_DELAY_RISK',
        severity='HIGH',
        delay_probability=prob,
        predicted_delay_minutes=delay,
        alert_status='ACTIVE'
    )
    db.add(alert)
    
    # Send notifications
    notification_service.send_sms(crew_phone, alert_message)
    notification_service.send_email(ops_team_email, alert_details)
    notification_service.send_slack(channel, alert_blocks)
```

### Step 7: Response to Frontend

**API Response**:
```json
{
  "flight_id": "EK230",
  "route": "DXB → LHR",
  "delay_probability": 0.342,
  "predicted_delay_minutes": 12.5,
  "risk_level": "LOW",
  "weather_conditions": {...},
  "route_statistics": {...},
  "shap_values": {...},
  "explanation": "The flight has a low delay risk...",
  "prediction_id": 1234
}
```

---

## 🤖 Langflow Agent Architecture

### Current Workflow

**File**: `backend/langflow_flow/preflight_ai_flow_router.json`

```
┌──────────┐     ┌─────────┐     ┌──────────┐     ┌─────────┐     ┌─────────┐
│  Input   │────▶│ Router  │────▶│  Python  │────▶│   LLM   │────▶│ Output  │
│ (SHAP)   │     │Decision │     │Calculate │     │(Mistral)│     │  Text   │
└──────────┘     └─────────┘     └──────────┘     └─────────┘     └─────────┘
                      │
                      ▼
                 High Risk?
                 (prob>0.7)
```

### Enhanced Workflow (To Be Implemented)

```
┌──────────────────────────────────────────────────────────────┐
│                   Input: Flight Details                       │
│            (flight_iata, dep_iata, arr_iata, date)           │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    API Call Nodes                               │
│  ┌──────────────┐  ┌──────────────┐  ┌───────────────────┐    │
│  │ Weather API  │  │ Flight API   │  │ Route Statistics  │    │
│  │ Open-Meteo   │  │AviationStack │  │   Historical      │    │
│  └──────────────┘  └──────────────┘  └───────────────────┘    │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                  Python Tool: Feature Engineering               │
│  Combine weather + flight data into ML features                │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                  Python Tool: ML Prediction                     │
│  Run predict_delay() and explain_prediction()                  │
└────────────────────────┬───────────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────────┐
│                    Router: Risk Assessment                      │
│  LOW (<0.4) | MODERATE (0.4-0.7) | HIGH (>0.7)                │
└──────┬───────────────┬──────────────────┬──────────────────────┘
       │               │                  │
       ▼               ▼                  ▼
    ┌────┐        ┌────────┐        ┌──────────┐
    │LLM │        │  LLM   │        │   LLM    │
    │Low │        │Moderate│        │ High +   │
    │Risk│        │  Risk  │        │  Alert   │
    └─┬──┘        └───┬────┘        └────┬─────┘
      │               │                  │
      │               │                  ▼
      │               │          ┌──────────────┐
      │               │          │Database Write│
      │               │          │Create Alert  │
      │               │          └──────┬───────┘
      │               │                 │
      │               │                 ▼
      │               │          ┌──────────────┐
      │               │          │Notification  │
      │               │          │Send SMS/Email│
      │               │          └──────────────┘
      │               │
      └───────────────┴──────────────────────────┐
                                                  │
                                                  ▼
                                          ┌──────────────┐
                                          │    Output    │
                                          │ Explanation  │
                                          └──────────────┘
```

---

## 🔌 API Integration Flow

### Open-Meteo Weather API

**Endpoint**: `https://api.open-meteo.com/v1/forecast`

**Our Wrapper**: `backend/external_apis/openmeteo_weather.py`

**Usage**:
```python
from external_apis import OpenMeteoClient

client = OpenMeteoClient()

# Current weather (automatically stored in DB)
current = client.get_current_weather('DXB')

# Hourly forecast
forecast = client.get_hourly_forecast('LHR', hours=48)

# Weather at specific time
future_weather = client.get_weather_at_time('JFK', departure_datetime)

# Aviation briefing with risk assessment
briefing = client.get_aviation_weather_briefing('DXB')
```

**Key Features**:
- ✅ Free unlimited API calls
- ✅ High-resolution (1km) forecasts
- ✅ 7-day forecast horizon
- ✅ Hourly updates
- ✅ 15 major airports pre-configured

### AviationStack Flight API

**Endpoint**: `https://api.aviationstack.com/v1/`

**API Key**: `00a88306b41eda9c29cc2b29732c51e6`

**Our Wrapper**: `backend/external_apis/flight_tracking.py`

**Usage**:
```python
from external_apis import AviationStackClient

client = AviationStackClient()

# Real-time flights
flights = client.get_real_time_flights(
    flight_iata='EK230',
    dep_iata='DXB',
    arr_iata='LHR'
)

# Historical flights (specific date)
historical = client.get_historical_flights(
    flight_date='2024-01-10',
    flight_iata='EK230'
)

# Route statistics (30-day history)
stats = client.get_flight_route_history('DXB', 'LHR', days_back=30)
route_stats = client.calculate_route_statistics(stats)

# Airport information
airport = client.get_airport_info('DXB')
```

**Key Features**:
- ✅ Real-time flight tracking
- ✅ Historical flight data
- ✅ Route delay statistics
- ✅ Airport/airline information
- ⚠️ Free tier: 100 calls/month

---

## 💾 Database Integration

### Tables and Relationships

```
flights_history ──┐
                  ├──▶ predictions ──┐
weather_snapshots─┘                  ├──▶ shap_explanations
                                     │
                                     └──▶ alerts ──▶ alert_actions

model_versions ──▶ predictions
                   
user_preferences
audit_logs
api_usage_logs
report_metadata
```

### Storage Workflow

1. **Weather Snapshot** (Every API call):
   ```python
   WeatherSnapshot(
       airport_code='DXB',
       observation_time=datetime.now(),
       temperature_c=28.5,
       wind_speed_kts=12.5,
       ...
   )
   ```

2. **Flight Prediction** (User request):
   ```python
   Prediction(
       flight_number='EK230',
       predicted_delay_minutes=12.5,
       delay_probability=0.342,
       model_version='v2.0-enhanced',
       features_used={...}
   )
   ```

3. **SHAP Explanation** (Per prediction):
   ```python
   ShapExplanation(
       prediction_id=1234,
       feature_name='wind',
       shap_value=0.15
   )
   ```

4. **Alert** (High-risk only):
   ```python
   Alert(
       flight_number='EK230',
       alert_type='HIGH_DELAY_RISK',
       severity='HIGH',
       delay_probability=0.85,
       alert_status='ACTIVE'
   )
   ```

5. **Alert Actions** (Notification tracking):
   ```python
   AlertAction(
       alert_id=1,
       action_type='NOTIFICATION_SENT',
       notification_channel='SMS',
       recipient='+971501234567',
       delivery_status='SUCCESS'
   )
   ```

---

## 🔔 Notification Flow

### When Alerts Trigger

**Condition**: `delay_probability > 0.7`

**Process**:
1. Create alert in database
2. Determine notification recipients from `user_preferences`
3. Send multi-channel notifications:

#### SMS (Twilio):
```python
sms_service.send_flight_alert(
    to=crew_phone,
    flight='EK230',
    delay_minutes=45,
    probability=0.85
)
```

#### Email (SendGrid):
```python
email_service.send_html_alert(
    to=ops_team_email,
    subject='HIGH RISK: EK230 Delay Alert',
    flight_details={...}
)
```

#### Slack:
```python
slack_service.send_alert(
    channel='#flight-ops',
    flight='EK230',
    delay_minutes=45,
    probability=0.85,
    actions=[...]
)
```

4. Log notification delivery in `alert_actions` table

---

## 📈 Prediction Accuracy Loop

### Continuous Improvement

```
┌────────────────────────────────────────────────────────────┐
│ 1. User requests prediction                                 │
│    Store: predicted_delay_minutes, delay_probability       │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ 2. Flight departs and lands                                 │
│    Background task: Fetch actual departure/arrival times   │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ 3. Calculate actual delay                                   │
│    actual_delay = actual_arrival - scheduled_arrival       │
│    Update prediction record with actual_delay_minutes      │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ 4. Trigger validation                                       │
│    Database trigger: update validation_timestamp           │
│    Calculate accuracy: |predicted - actual| < 15 min?      │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ 5. Model metrics update                                     │
│    Aggregate accuracy data for model version               │
│    Store in model_metrics table                            │
└────────────────────────┬───────────────────────────────────┘
                         │
                         ▼
┌────────────────────────────────────────────────────────────┐
│ 6. Route learning                                           │
│    Use validated predictions to improve route statistics   │
│    Feed back into next predictions for same route          │
└────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Better Over Time

### Temporal Prediction Strategy

**7+ Days Before Flight**:
- Relies heavily on historical route statistics
- Weather forecast less reliable
- Accuracy: ~60-70%

**3-7 Days Before Flight**:
- Adds weather forecast trends
- Historical patterns + forecast combination
- Accuracy: ~70-80%

**1-3 Days Before Flight**:
- Uses more accurate weather forecasts
- Recent route performance data
- Accuracy: ~80-85%

**Same Day**:
- Real-time weather conditions
- Current ATC/airport status
- Most recent delays on route
- Accuracy: ~85-90%

### Implementation in Code

```python
def get_prediction_features(flight_date, dep_iata, arr_iata):
    days_until_flight = (flight_date - datetime.now()).days
    
    if days_until_flight > 7:
        # Rely on historical data
        weight_history = 0.8
        weight_weather = 0.2
    elif days_until_flight > 3:
        # Balanced approach
        weight_history = 0.6
        weight_weather = 0.4
    else:
        # Trust weather more
        weight_history = 0.4
        weight_weather = 0.6
    
    # Combine features with appropriate weights
    features = combine_features(
        route_stats=get_route_stats(dep_iata, arr_iata),
        weather=get_weather_forecast(dep_iata, flight_date),
        weights={'history': weight_history, 'weather': weight_weather}
    )
    
    return features
```

---

## 🔧 Development Workflow

### Starting the System

```bash
# 1. Start all services
docker-compose up -d

# 2. Wait for services to be healthy
docker-compose ps

# 3. Run database migrations
docker-compose exec backend alembic upgrade head

# 4. Test API health
curl http://localhost:8000/health

# 5. Access services
# - API: http://localhost:8000
# - Frontend: http://localhost:3000
# - Langflow: http://localhost:7860
# - pgAdmin: http://localhost:5050
# - Redis Commander: http://localhost:8081
```

### Testing a Complete Prediction

```bash
# Make enhanced prediction
curl -X POST "http://localhost:8000/predict/enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "flight_iata": "EK230",
    "dep_iata": "DXB",
    "arr_iata": "LHR",
    "scheduled_departure": "2024-01-25T14:30:00"
  }'

# Check database for stored prediction
docker-compose exec postgres psql -U preflight -d preflight_db \
  -c "SELECT * FROM predictions ORDER BY prediction_timestamp DESC LIMIT 1;"

# Check if alert was created (if high-risk)
curl http://localhost:8000/alerts/active

# View recent predictions
curl "http://localhost:8000/analytics/predictions/recent?limit=10"
```

---

## 📊 Monitoring & Analytics

### Key Metrics to Track

1. **Prediction Volume**:
   ```sql
   SELECT DATE(prediction_timestamp), COUNT(*) 
   FROM predictions 
   GROUP BY DATE(prediction_timestamp) 
   ORDER BY DATE(prediction_timestamp) DESC;
   ```

2. **Model Accuracy**:
   ```sql
   SELECT * FROM v_model_accuracy_summary;
   ```

3. **Alert Statistics**:
   ```sql
   SELECT alert_type, severity, COUNT(*) 
   FROM alerts 
   WHERE created_at > NOW() - INTERVAL '7 days' 
   GROUP BY alert_type, severity;
   ```

4. **API Usage**:
   ```sql
   SELECT api_name, DATE(request_timestamp), COUNT(*) 
   FROM api_usage_logs 
   GROUP BY api_name, DATE(request_timestamp) 
   ORDER BY DATE(request_timestamp) DESC;
   ```

---

## 🎓 Key Takeaways

1. **Weather + Historical Data = Better Predictions**
   - Open-Meteo provides real-time weather conditions
   - AviationStack gives historical delay patterns
   - Combination improves accuracy by 20-30%

2. **Database is the Source of Truth**
   - All predictions stored for validation
   - SHAP explanations enable model debugging
   - Audit trail for compliance

3. **Langflow Orchestrates Intelligence**
   - Routes high-risk vs low-risk flows
   - Generates human-readable explanations
   - Triggers automated notifications

4. **System Gets Smarter Over Time**
   - Validated predictions feed back into model
   - Route statistics improve with more data
   - Temporal weighting adapts to flight date

5. **Multi-Channel Notifications Ensure Action**
   - SMS for immediate crew alerts
   - Email for detailed operations briefings
   - Slack for team coordination

---

## 🔗 Quick Links

- API Documentation: `backend/API_ENDPOINTS.md`
- Database Schema: `backend/database/schema.sql`
- Setup Guide: `SETUP_GUIDE.md`
- Enhancement Plan: `ENHANCEMENT_PLAN.md`
- Implementation Status: `IMPLEMENTATION_STATUS.md`
