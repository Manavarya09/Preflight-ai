from pydantic import BaseModel


class FlightRecord(BaseModel):
    flight_id: str
    scheduled_departure: str
    scheduled_arrival: str
    weather: dict
    gate: str
    atc: str
