import os
import joblib
import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "models")

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "airshield_xgboost.pkl"
)

PREPROCESSOR_PATH = os.path.join(
    MODEL_DIR,
    "airshield_preprocessor.pkl"
)


# ============================================================
# LOAD MODEL
# ============================================================

model = joblib.load(MODEL_PATH)
preprocessor = joblib.load(PREPROCESSOR_PATH)


# ============================================================
# PREDICTION FUNCTION
# ============================================================

def predict_aqi(data: dict):

    # Convert input dictionary to DataFrame
    input_df = pd.DataFrame([data])

    # Transform using the exact preprocessing pipeline
    processed_data = preprocessor.transform(input_df)

    # Predict AQI
    prediction = model.predict(processed_data)[0]

    return float(prediction)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_data = {
        "area": "Amritsar",
        "season": "Winter",

        "fireCount": 5,

        "temperature_2m_mean": 15.0,
        "temperature_2m_max": 20.0,
        "temperature_2m_min": 10.0,
        "relative_humidity_2m_mean": 70.0,
        "precipitation_sum": 0.0,
        "wind_speed_10m_max": 10.0,
        "surface_pressure_mean": 1005.0,

        "month": 12,
        "day_of_year": 350,
        "year": 2023,

        "aqi_lag_1d": 118.0,
        "aqi_lag_3d": 125.0,
        "aqi_lag_7d": 110.0,

        "aqi_rolling_3d": 120.0,
        "aqi_rolling_7d": 117.0,
        "aqi_rolling_14d": 115.0
    }

    prediction = predict_aqi(sample_data)

    print(f"Predicted AQI: {prediction:.2f}")