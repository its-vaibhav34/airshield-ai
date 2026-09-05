from datetime import date

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from ml.predict import predict_aqi

from backend.aqi_features import (
    get_aqi_history_features
)

from backend.fire_forecast import (
    get_future_fire_feature
)

from backend.weather_forecast import (
    get_future_weather_features
)

from backend.cpcb_service import (
    get_live_cpcb_data
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="AirShield AI",
    description="AQI Prediction and Live Air Quality API",
    version="1.0.0"
)


# ============================================================
# REQUEST MODEL
# ============================================================

class AQIRequest(BaseModel):

    area: str
    date: date


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

    target_date = request.date

    # --------------------------------------------------------
    # Date features
    # --------------------------------------------------------

    month = target_date.month

    day_of_year = target_date.timetuple().tm_yday

    year = target_date.year

    season = get_season(month)


    # --------------------------------------------------------
    # Historical AQI features
    #
    # These use ONLY AQI observations before target date.
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
    # Future fire estimate
    #
    # IMPORTANT:
    # Do NOT use actual future fire observations.
    # --------------------------------------------------------

    try:

        fire_feature = get_future_fire_feature(
            request.area,
            target_date
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Future fire estimation failed: {str(e)}"
        )


    # --------------------------------------------------------
    # Future weather forecast
    #
    # IMPORTANT:
    # Weather must come from forecast data.
    # --------------------------------------------------------

    try:

        weather_features = get_future_weather_features(
            request.area,
            target_date
        )

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=502,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Weather forecast failed: {str(e)}"
        )


    # --------------------------------------------------------
    # Build final model input
    #
    # Must match the saved model's expected features.
    # --------------------------------------------------------

    input_data = {

        # Location
        "area": request.area,

        # Season
        "season": season,

        # Future-safe fire estimate
        **fire_feature,

        # Future weather forecast
        **weather_features,

        # Calendar features
        "month": month,
        "day_of_year": day_of_year,
        "year": year,

        # Historical AQI features
        **historical_features
    }


    # --------------------------------------------------------
    # Predict AQI
    # --------------------------------------------------------

    try:

        prediction = predict_aqi(
            input_data
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"AQI prediction failed: {str(e)}"
        )


    # --------------------------------------------------------
    # AQI category
    # --------------------------------------------------------

    category = get_aqi_category(
        prediction
    )


    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {

        "area": request.area,

        "date": str(request.date),

        "predicted_aqi": round(
            prediction,
            2
        ),

        "category": category
    }


# ============================================================
# LIVE CPCB AIR QUALITY
# ============================================================

@app.get("/live-aqi/{area}")
def live_aqi(area: str):

    try:

        live_data = get_live_cpcb_data(
            area
        )

        return live_data

    except ValueError as e:

        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=502,
            detail=str(e)
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Live AQI service failed: {str(e)}"
        )