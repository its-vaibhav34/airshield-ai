from fastapi import FastAPI
from pydantic import BaseModel, Field
from ml.predict import predict_aqi


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AirShield AI",
    description="AQI Prediction API",
    version="1.0.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class AQIRequest(BaseModel):

    area: str
    season: str

    fireCount: float

    temperature_2m_mean: float
    temperature_2m_max: float
    temperature_2m_min: float

    relative_humidity_2m_mean: float

    precipitation_sum: float

    wind_speed_10m_max: float

    surface_pressure_mean: float

    month: int = Field(ge=1, le=12)
    day_of_year: int = Field(ge=1, le=366)
    year: int

    aqi_lag_1d: float
    aqi_lag_3d: float
    aqi_lag_7d: float

    aqi_rolling_3d: float
    aqi_rolling_7d: float
    aqi_rolling_14d: float


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "AirShield AI API is running",
        "status": "online"
    }


# ============================================================
# AQI CATEGORY
# ============================================================

def get_aqi_category(aqi: float):

    if aqi <= 50:
        return "Good"

    elif aqi <= 100:
        return "Satisfactory"

    elif aqi <= 200:
        return "Moderate"

    elif aqi <= 300:
        return "Poor"

    elif aqi <= 400:
        return "Very Poor"

    else:
        return "Severe"


# ============================================================
# PREDICTION ENDPOINT
# ============================================================

@app.post("/predict")
def predict(request: AQIRequest):

    input_data = request.model_dump()

    prediction = predict_aqi(input_data)

    category = get_aqi_category(prediction)

    return {
        "area": request.area,
        "predicted_aqi": round(prediction, 2),
        "category": category
    }