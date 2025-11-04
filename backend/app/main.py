from fastapi import BackgroundTasks, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.models.explain import explain_prediction
from app.models.predictor import predict_delay
from app.schemas.flight import FlightRecord
from app.services.langflow_client import generate_explanation

app = FastAPI(title="PreFlight AI API", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "PreFlight AI backend running"}


@app.get("/flights")
def get_flights():
    return [
        {
            "flight_id": "EK230",
            "origin": "DXB",
            "dest": "LHR",
            "delay_prob": 0.78,
            "status": "likely delayed",
        },
        {
            "flight_id": "AI101",
            "origin": "DEL",
            "dest": "DXB",
            "delay_prob": 0.21,
            "status": "on-time",
        },
    ]


@app.post("/score")
def score_flight(record: FlightRecord, background_tasks: BackgroundTasks):
    features = {
        "wind": record.weather.get("wind_kts", 0),
        "visibility": record.weather.get("visibility_km", 10),
        "atc": len(record.atc),
    }
    prob, delay = predict_delay(features)
    shap = explain_prediction(features)
    explanation = generate_explanation(shap)
    return {
        "flight_id": record.flight_id,
        "delay_prob": prob,
        "predicted_delay_minutes": delay,
        "shap": shap,
        "explanation": explanation,
    }


@app.get("/insights")
def insights():
    return generate_explanation(
        {"crosswind": 0.2, "gate_congestion": 0.17, "route_delay": 0.14}
    )
