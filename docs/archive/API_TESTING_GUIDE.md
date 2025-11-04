# 🧪 PreFlight AI - API Testing Guide

Quick reference for testing all the new enhanced features.

## 📡 Base URL
```
http://localhost:5000
```

---

## 🏥 Health Checks

### Check Backend Status
```bash
curl http://localhost:5000/
```

### Check Database Connections
```bash
curl http://localhost:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "database": {
    "postgresql": {"connected": true},
    "redis": {"connected": true}
  },
  "services": {
    "langflow": "connected",
    "ollama": "connected"
  }
}
```

---

## ✈️ Flight Operations

### Get All Flights
```bash
curl http://localhost:5000/flights
```

### Get Single Flight
```bash
curl http://localhost:5000/flights/EK230
```

### Score a Flight (Predict Delay)
```bash
curl -X POST http://localhost:5000/score \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "EK230",
    "scheduled_departure": "2025-11-05T10:30:00Z",
    "scheduled_arrival": "2025-11-05T14:30:00Z",
    "weather": {
      "wind_kts": 18,
      "visibility_km": 6,
      "precipitation_mm": 2.5
    },
    "gate": "A12",
    "atc": "ground hold extension"
  }'
```

**Expected Response:**
```json
{
  "flight_id": "EK230",
  "delay_prob": 0.78,
  "predicted_delay_minutes": 23,
  "confidence_score": 0.92,
  "shap": {
    "crosswind": 0.23,
    "visibility": -0.12,
    "atc": 0.09
  },
  "explanation": "This flight faces significant delay risk (78% probability)...",
  "stored_in_database": true,
  "prediction_id": "uuid-here"
}
```

---

## 🌤️ Weather Data

### Get Current Weather for Airport
```bash
curl http://localhost:5000/weather/current/DXB
```

### Get Weather Forecast
```bash
curl http://localhost:5000/weather/forecast/DXB?hours=48
```

**Expected Response:**
```json
{
  "airport_code": "DXB",
  "timestamp": "2025-11-05T08:30:00Z",
  "temperature_c": 32.5,
  "wind_speed_kts": 12.5,
  "wind_direction_deg": 270,
  "visibility_km": 10.0,
  "precipitation_type": "NONE",
  "thunderstorm_nearby": false,
  "data_source": "OPENWEATHERMAP"
}
```

---

## 🔔 Alerts Management

### Get Active Alerts
```bash
curl http://localhost:5000/alerts/active
```

### Get Alerts for Specific Flight
```bash
curl http://localhost:5000/alerts/flight/EK230
```

### Acknowledge an Alert
```bash
curl -X POST http://localhost:5000/alerts/{alert_id}/acknowledge \
  -H "Content-Type: application/json" \
  -d '{
    "acknowledged_by": "operator_john",
    "comment": "Crew has been notified"
  }'
```

### Escalate an Alert
```bash
curl -X POST http://localhost:5000/alerts/{alert_id}/escalate \
  -H "Content-Type: application/json" \
  -d '{
    "escalated_by": "supervisor_jane",
    "reason": "Delay exceeds 45 minutes"
  }'
```

---

## 📧 Notifications

### Send SMS Alert to Crew
```bash
curl -X POST http://localhost:5000/notifications/sms \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "EK230",
    "delay_minutes": 25,
    "phone_number": "+1234567890",
    "message_type": "crew_alert"
  }'
```

### Send Email to Operations Team
```bash
curl -X POST http://localhost:5000/notifications/email \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "EK230",
    "delay_prob": 0.78,
    "predicted_delay": 23,
    "recipients": ["ops@airline.com", "manager@airline.com"],
    "include_details": true
  }'
```

### Post to Slack Channel
```bash
curl -X POST http://localhost:5000/notifications/slack \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "EK230",
    "delay_prob": 0.78,
    "predicted_delay": 23,
    "alert_type": "high_risk"
  }'
```

### Send Multi-Channel Alert
```bash
curl -X POST http://localhost:5000/notifications/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "flight_id": "EK230",
    "channels": ["sms", "email", "slack"],
    "crew_phone": "+1234567890",
    "ops_emails": ["ops@airline.com"]
  }'
```

---

## 📊 Analytics & Reporting

### Get Daily Operations Summary
```bash
curl http://localhost:5000/analytics/daily/2025-11-05
```

**Expected Response:**
```json
{
  "date": "2025-11-05",
  "total_flights": 247,
  "predictions_made": 245,
  "alerts_triggered": 18,
  "critical_alerts": 3,
  "avg_delay_probability": 0.42,
  "avg_actual_delay": 15.3,
  "delayed_flights": 89,
  "delay_percentage": 36.03,
  "model_accuracy": 94.2
}
```

### Get Model Performance Metrics
```bash
curl http://localhost:5000/analytics/model/performance
```

### Get Prediction Accuracy Over Time
```bash
curl http://localhost:5000/analytics/accuracy?days=30
```

### Get Top Delay Factors
```bash
curl http://localhost:5000/analytics/factors/top
```

---

## 📄 Reports

### Generate Daily Report (PDF)
```bash
curl -X POST http://localhost:5000/reports/daily/generate \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-11-05",
    "format": "pdf"
  }'
```

**Response:**
```json
{
  "report_id": "uuid-here",
  "file_path": "/app_data/reports/daily/report_2025-11-05.pdf",
  "download_url": "http://localhost:5000/reports/download/uuid-here",
  "generated_at": "2025-11-05T23:59:00Z"
}
```

### Download Report
```bash
curl http://localhost:5000/reports/download/{report_id} \
  --output daily_report.pdf
```

### Export Data to CSV
```bash
curl -X POST http://localhost:5000/reports/export/csv \
  -H "Content-Type: application/json" \
  -d '{
    "start_date": "2025-11-01",
    "end_date": "2025-11-05",
    "include": ["predictions", "weather", "shap_values"]
  }' \
  --output predictions_export.csv
```

---

## 🤖 AI & Model Management

### Get Active Model Info
```bash
curl http://localhost:5000/model/active
```

### Get All Model Versions
```bash
curl http://localhost:5000/model/versions
```

### Get Model Accuracy Comparison
```bash
curl http://localhost:5000/model/compare
```

### Trigger Model Retraining (Admin Only)
```bash
curl -X POST http://localhost:5000/model/retrain \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer your_admin_token" \
  -d '{
    "training_start_date": "2025-01-01",
    "training_end_date": "2025-10-31",
    "model_type": "LSTM_XGBOOST"
  }'
```

---

## 🔍 Search & Query

### Search Flights by Criteria
```bash
curl -X POST http://localhost:5000/flights/search \
  -H "Content-Type: application/json" \
  -d '{
    "origin": "DXB",
    "destination": "LHR",
    "date_from": "2025-11-01",
    "date_to": "2025-11-30",
    "min_delay_prob": 0.6
  }'
```

### Get Historical Predictions for Flight
```bash
curl http://localhost:5000/flights/EK230/history?days=30
```

### Get Flights with High Delay Risk
```bash
curl http://localhost:5000/flights/high-risk?threshold=0.7
```

---

## 💾 Cache Operations

### Get Cached Prediction
```bash
curl http://localhost:5000/cache/prediction/EK230
```

### Clear Cache for Flight
```bash
curl -X DELETE http://localhost:5000/cache/flight/EK230
```

### Get Cache Statistics
```bash
curl http://localhost:5000/cache/stats
```

---

## 🔐 Admin Operations

### Get System Status
```bash
curl http://localhost:5000/admin/status \
  -H "Authorization: Bearer your_admin_token"
```

### Get API Usage Statistics
```bash
curl http://localhost:5000/admin/api-usage?days=7 \
  -H "Authorization: Bearer your_admin_token"
```

### Get Cost Report
```bash
curl http://localhost:5000/admin/costs?month=2025-11 \
  -H "Authorization: Bearer your_admin_token"
```

### View Audit Logs
```bash
curl http://localhost:5000/admin/audit-logs?limit=100 \
  -H "Authorization: Bearer your_admin_token"
```

---

## 🧪 Testing with Python

```python
import requests

BASE_URL = "http://localhost:5000"

# Score a flight
response = requests.post(
    f"{BASE_URL}/score",
    json={
        "flight_id": "TEST123",
        "scheduled_departure": "2025-11-05T10:00:00Z",
        "scheduled_arrival": "2025-11-05T14:00:00Z",
        "weather": {"wind_kts": 18, "visibility_km": 6},
        "gate": "A12",
        "atc": "ground hold"
    }
)

print(response.json())
```

---

## 🧪 Testing with Postman

1. Import the Postman collection (if provided)
2. Set environment variable: `base_url = http://localhost:5000`
3. Run the entire collection to test all endpoints

---

## 📝 Notes

- **Authentication**: Most endpoints require authentication in production
- **Rate Limiting**: Some endpoints are rate-limited (60 requests/minute by default)
- **Data Persistence**: All predictions and alerts are stored in PostgreSQL
- **Cache TTL**: Redis cache expires after 5 minutes for flights, 10 minutes for weather
- **Async Operations**: Report generation happens asynchronously; check status endpoint

---

## 🐛 Debugging Tips

### Check Recent Logs
```bash
docker-compose logs --tail=50 backend
```

### Test Database Connection
```bash
docker-compose exec postgres psql -U preflight -d preflight_db -c "SELECT COUNT(*) FROM predictions;"
```

### Test Redis Connection
```bash
docker-compose exec redis redis-cli PING
```

### Check Langflow Connection
```bash
curl http://localhost:7860/health
```

---

Happy Testing! 🚀
