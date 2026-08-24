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

AQI_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "data",
    "processed",
    "cleaned_punjab_aqi.csv"
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
# LOAD AQI DATA
# ============================================================

aqi_df = pd.read_csv(AQI_PATH)

aqi_df["date"] = pd.to_datetime(
    aqi_df["date"]
)

# Keep only areas used by final model
aqi_df = aqi_df[
    aqi_df["area"].isin(MODEL_AREAS)
].copy()


# ============================================================
# SORT
# ============================================================

aqi_df = (
    aqi_df
    .sort_values(["area", "date"])
    .reset_index(drop=True)
)


# ============================================================
# CREATE DATE-BASED AQI LOOKUP
# ============================================================

aqi_lookup = (
    aqi_df
    .drop_duplicates(
        subset=["area", "date"],
        keep="last"
    )
    .set_index(["area", "date"])["aqi_value"]
)


# ============================================================
# HISTORICAL AQI FEATURES
# ============================================================

def get_aqi_history_features(
    area: str,
    target_date
):

    target_date = pd.Timestamp(
        target_date
    )

    if area not in MODEL_AREAS:
        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {MODEL_AREAS}"
        )


    # --------------------------------------------------------
    # Get all historical AQI before target date
    # --------------------------------------------------------

    area_history = aqi_df[
        (aqi_df["area"] == area) &
        (aqi_df["date"] < target_date)
    ].copy()

    area_history = (
        area_history
        .sort_values("date")
        .reset_index(drop=True)
    )


    if area_history.empty:
        raise ValueError(
            f"No historical AQI available for "
            f"{area} before {target_date.date()}"
        )


    # --------------------------------------------------------
    # Date → AQI dictionary
    # --------------------------------------------------------

    history = (
        area_history
        .set_index("date")["aqi_value"]
    )


    # --------------------------------------------------------
    # Calendar-date lags
    # --------------------------------------------------------

    lag_1_date = target_date - pd.Timedelta(days=1)
    lag_3_date = target_date - pd.Timedelta(days=3)
    lag_7_date = target_date - pd.Timedelta(days=7)


    aqi_lag_1d = history.get(
        lag_1_date,
        float("nan")
    )

    aqi_lag_3d = history.get(
        lag_3_date,
        float("nan")
    )

    aqi_lag_7d = history.get(
        lag_7_date,
        float("nan")
    )


    # --------------------------------------------------------
    # Rolling historical AQI
    #
    # Use only observations BEFORE target date.
    # Current target day's AQI is never included.
    # --------------------------------------------------------

    past_values = area_history["aqi_value"]


    aqi_rolling_3d = (
        past_values
        .tail(3)
        .mean()
    )

    aqi_rolling_7d = (
        past_values
        .tail(7)
        .mean()
    )

    aqi_rolling_14d = (
        past_values
        .tail(14)
        .mean()
    )


    return {
        "aqi_lag_1d": float(aqi_lag_1d),
        "aqi_lag_3d": float(aqi_lag_3d),
        "aqi_lag_7d": float(aqi_lag_7d),

        "aqi_rolling_3d": float(aqi_rolling_3d),
        "aqi_rolling_7d": float(aqi_rolling_7d),
        "aqi_rolling_14d": float(aqi_rolling_14d)
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_area = "Amritsar"
    test_date = "2024-01-15"

    features = get_aqi_history_features(
        test_area,
        test_date
    )

    print("=" * 60)
    print("AQI HISTORICAL FEATURES")
    print("=" * 60)

    print("Area:", test_area)
    print("Date:", test_date)

    for key, value in features.items():
        print(f"{key}: {value}")