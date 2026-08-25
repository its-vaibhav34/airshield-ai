import os
import pandas as pd


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

WEATHER_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "data",
    "external",
    "weather_data.csv"
)


# ============================================================
# MODEL AREAS
# ============================================================

MODEL_AREAS = [
    "Amritsar",
    "Bathinda",
    "Jalandhar",
    "Ludhiana",
    "Patiala",
    "Rupnagar"
]


# ============================================================
# WEATHER FEATURES
# ============================================================

WEATHER_COLUMNS = [
    "temperature_2m_mean",
    "temperature_2m_max",
    "temperature_2m_min",
    "relative_humidity_2m_mean",
    "precipitation_sum",
    "wind_speed_10m_max",
    "surface_pressure_mean"
]


# ============================================================
# LOAD WEATHER DATA
# ============================================================

weather_df = pd.read_csv(WEATHER_PATH)

weather_df["date"] = pd.to_datetime(
    weather_df["date"]
)


# ============================================================
# KEEP ONLY MODEL AREAS
# ============================================================

weather_df = weather_df[
    weather_df["area"].isin(MODEL_AREAS)
].copy()


# ============================================================
# SORT
# ============================================================

weather_df = (
    weather_df
    .sort_values(["area", "date"])
    .reset_index(drop=True)
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

weather_df = (
    weather_df
    .drop_duplicates(
        subset=["area", "date"],
        keep="last"
    )
    .reset_index(drop=True)
)


# ============================================================
# WEATHER LOOKUP
# ============================================================

weather_lookup = (
    weather_df
    .set_index(["area", "date"])[WEATHER_COLUMNS]
)


# ============================================================
# GET WEATHER FEATURES
# ============================================================

def get_weather_features(
    area: str,
    target_date
):

    target_date = pd.Timestamp(
        target_date
    )


    # --------------------------------------------------------
    # Validate area
    # --------------------------------------------------------

    if area not in MODEL_AREAS:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {MODEL_AREAS}"
        )


    # --------------------------------------------------------
    # Exact date lookup
    # --------------------------------------------------------

    try:

        weather_values = weather_lookup.loc[
            (area, target_date)
        ]

    except KeyError:

        raise ValueError(
            f"No weather data available for "
            f"{area} on {target_date.date()}"
        )


    # --------------------------------------------------------
    # Check missing values
    # --------------------------------------------------------

    if weather_values.isna().any():

        missing_columns = (
            weather_values[
                weather_values.isna()
            ]
            .index
            .tolist()
        )

        raise ValueError(
            f"Missing weather values for "
            f"{area} on {target_date.date()}: "
            f"{missing_columns}"
        )


    # --------------------------------------------------------
    # Return model-ready dictionary
    # --------------------------------------------------------

    return {
        column: float(weather_values[column])
        for column in WEATHER_COLUMNS
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_area = "Amritsar"
    test_date = "2024-01-15"

    features = get_weather_features(
        test_area,
        test_date
    )

    print("=" * 60)
    print("WEATHER FEATURES")
    print("=" * 60)

    print("Area:", test_area)
    print("Date:", test_date)

    for key, value in features.items():
        print(f"{key}: {value}")