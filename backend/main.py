from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ml.predict import predict_aqi
from backend.aqi_features import get_aqi_history_features


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
    date: date

    fireCount: float

    temperature_2m_mean: float
    temperature_2m_max: float
    temperature_2m_min: float

    relative_humidity_2m_mean: float

    precipitation_sum: float

    wind_speed_10m_max: float

    surface_pressure_mean: float


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
# SEASON
# ============================================================

def get_season(month: int):

    if month in [12, 1, 2]:
        return "Winter"

    elif month in [3, 4, 5]:
        return "Summer"

    elif month in [6, 7, 8, 9]:
        return "Monsoon"

    else:
        return "Post-Monsoon"


# ============================================================
# AQI PREDICTION
# ============================================================

@app.post("/predict")
def predict(request: AQIRequest):

    # --------------------------------------------------------
    # Date features
    # --------------------------------------------------------

    target_date = request.date

    month = target_date.month

    day_of_year = target_date.timetuple().tm_yday

    year = target_date.year

    season = get_season(month)


    # --------------------------------------------------------
    # Automatically calculate historical AQI features
    # --------------------------------------------------------

    try:

        historical_features = get_aqi_history_features(
            request.area,
            target_date
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )


    # --------------------------------------------------------
    # Build final model input
    # --------------------------------------------------------

    input_data = {

        "area": request.area,
        "season": season,

        "fireCount": request.fireCount,

        "temperature_2m_mean":
            request.temperature_2m_mean,

        "temperature_2m_max":
            request.temperature_2m_max,

        "temperature_2m_min":
            request.temperature_2m_min,

        "relative_humidity_2m_mean":
            request.relative_humidity_2m_mean,

        "precipitation_sum":
            request.precipitation_sum,

        "wind_speed_10m_max":
            request.wind_speed_10m_max,

        "surface_pressure_mean":
            request.surface_pressure_mean,

        "month": month,
        "day_of_year": day_of_year,
        "year": year,

        # Automatically generated historical AQI features
        **historical_features
    }


    # --------------------------------------------------------
    # Predict AQI
    # --------------------------------------------------------

    prediction = predict_aqi(input_data)

    category = get_aqi_category(prediction)


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "area": request.area,

        "date": str(request.date),

        "predicted_aqi":
            round(prediction, 2),

        "category": category
    }