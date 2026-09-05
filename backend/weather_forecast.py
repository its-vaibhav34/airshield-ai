import requests
import pandas as pd


# ============================================================
# MODEL AREAS + COORDINATES
# ============================================================

AREA_COORDINATES = {

    "Amritsar": {
        "latitude": 31.6200,
        "longitude": 74.8765
    },

    "Bathinda": {
        "latitude": 30.2110,
        "longitude": 74.9455
    },

    "Jalandhar": {
        "latitude": 31.3260,
        "longitude": 75.5762
    },

    "Ludhiana": {
        "latitude": 30.9010,
        "longitude": 75.8573
    },

    "Patiala": {
        "latitude": 30.3398,
        "longitude": 76.3869
    },

    "Rupnagar": {
        "latitude": 30.9660,
        "longitude": 76.5330
    }
}


# ============================================================
# OPEN-METEO API
# ============================================================

API_URL = "https://api.open-meteo.com/v1/forecast"


# ============================================================
# GET FUTURE WEATHER FEATURES
# ============================================================

def get_future_weather_features(
    area: str,
    target_date
):

    # --------------------------------------------------------
    # Validate area
    # --------------------------------------------------------

    if area not in AREA_COORDINATES:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: "
            f"{list(AREA_COORDINATES.keys())}"
        )


    target_date = pd.Timestamp(
        target_date
    ).strftime("%Y-%m-%d")


    coordinates = AREA_COORDINATES[area]


    # --------------------------------------------------------
    # Request daily forecast
    # --------------------------------------------------------

    params = {

        "latitude":
            coordinates["latitude"],

        "longitude":
            coordinates["longitude"],

        "daily": ",".join([

            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "relative_humidity_2m_mean",
            "precipitation_sum",
            "wind_speed_10m_max",
            "surface_pressure_mean"

        ]),

        "start_date": target_date,
        "end_date": target_date,

        "timezone": "Asia/Kolkata",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }


    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=(10, 30)
        )

    except requests.exceptions.RequestException as e:

        raise RuntimeError(
            f"Weather forecast request failed: {e}"
        )


    # --------------------------------------------------------
    # HTTP ERROR
    # --------------------------------------------------------

    if not response.ok:

        raise RuntimeError(
            f"Open-Meteo returned HTTP "
            f"{response.status_code}: "
            f"{response.text[:300]}"
        )


    data = response.json()


    # --------------------------------------------------------
    # Validate response
    # --------------------------------------------------------

    daily = data.get("daily")

    if not daily:

        raise RuntimeError(
            f"No daily weather data returned "
            f"for {area} on {target_date}"
        )


    if not daily.get("time"):

        raise RuntimeError(
            f"No forecast date returned "
            f"for {area} on {target_date}"
        )


    # --------------------------------------------------------
    # Extract first/only requested date
    # --------------------------------------------------------

    result = {

        "temperature_2m_mean":
            daily["temperature_2m_mean"][0],

        "temperature_2m_max":
            daily["temperature_2m_max"][0],

        "temperature_2m_min":
            daily["temperature_2m_min"][0],

        "relative_humidity_2m_mean":
            daily["relative_humidity_2m_mean"][0],

        "precipitation_sum":
            daily["precipitation_sum"][0],

        "wind_speed_10m_max":
            daily["wind_speed_10m_max"][0],

        "surface_pressure_mean":
            daily["surface_pressure_mean"][0]
    }


    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    missing = [
        key
        for key, value in result.items()
        if value is None
    ]


    if missing:

        raise RuntimeError(
            f"Missing weather forecast values "
            f"for {area} on {target_date}: "
            f"{missing}"
        )


    # --------------------------------------------------------
    # Convert values to float
    # --------------------------------------------------------

    return {
        key: float(value)
        for key, value in result.items()
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_area = "Amritsar"
    test_date = "2026-08-26"

    print("=" * 65)
    print("AIRSHIELD FUTURE WEATHER TEST")
    print("=" * 65)

    print("Area:", test_area)
    print("Date:", test_date)

    features = get_future_weather_features(
        test_area,
        test_date
    )

    print("\nForecast weather features:")
    print("-" * 65)

    for key, value in features.items():

        print(
            f"{key:<30} : {value}"
        )

    print("-" * 65)
    print("TEST COMPLETE")
    print("=" * 65)