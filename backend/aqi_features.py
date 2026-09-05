import pandas as pd

from backend.aqi_history import (
    MODEL_AREAS,
    get_aqi_history,
)


# ============================================================
# HISTORICAL AQI FEATURES
# ============================================================

def get_aqi_history_features(
    area: str,
    target_date
):

    # --------------------------------------------------------
    # Validate area
    # --------------------------------------------------------

    if area not in MODEL_AREAS:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {MODEL_AREAS}"
        )


    # --------------------------------------------------------
    # Normalize target date
    # --------------------------------------------------------

    target_date = pd.Timestamp(
        target_date
    )


    # --------------------------------------------------------
    # Load unified AQI history
    #
    # This combines:
    #
    # 1. Historical AQI dataset
    # 2. CPCB live AQI history
    # --------------------------------------------------------

    all_history = get_aqi_history()


    # --------------------------------------------------------
    # Get only this area's observations BEFORE target date
    #
    # Target day's AQI is NEVER included.
    # --------------------------------------------------------

    area_history = all_history[
        (all_history["area"] == area)
        &
        (all_history["date"] < target_date)
    ].copy()


    area_history = (
        area_history
        .sort_values("date")
        .reset_index(drop=True)
    )


    # --------------------------------------------------------
    # Need at least some historical observations
    # --------------------------------------------------------

    if area_history.empty:

        raise ValueError(
            f"No AQI history available for "
            f"{area} before {target_date.date()}"
        )


    # --------------------------------------------------------
    # Date → AQI lookup
    # --------------------------------------------------------

    history = (
        area_history
        .set_index("date")["aqi_value"]
    )


    # ========================================================
    # CALENDAR-DATE LAGS
    # ========================================================

    lag_1_date = (
        target_date
        - pd.Timedelta(days=1)
    )

    lag_3_date = (
        target_date
        - pd.Timedelta(days=3)
    )

    lag_7_date = (
        target_date
        - pd.Timedelta(days=7)
    )


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


    # ========================================================
    # ROLLING FEATURES
    #
    # IMPORTANT:
    # These use only observations BEFORE target_date.
    #
    # We do NOT include target day's AQI.
    # ========================================================

    past_values = (
        area_history["aqi_value"]
    )


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


    # ========================================================
    # RETURN MODEL FEATURES
    # ========================================================

    return {

        "aqi_lag_1d":
            float(aqi_lag_1d),

        "aqi_lag_3d":
            float(aqi_lag_3d),

        "aqi_lag_7d":
            float(aqi_lag_7d),

        "aqi_rolling_3d":
            float(aqi_rolling_3d),

        "aqi_rolling_7d":
            float(aqi_rolling_7d),

        "aqi_rolling_14d":
            float(aqi_rolling_14d),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("AQI FUTURE FEATURE TEST")
    print("=" * 60)


    # --------------------------------------------------------
    # Test 1: Historical date
    # --------------------------------------------------------

    test_area = "Amritsar"
    test_date = "2024-01-15"


    print("\nHistorical test")
    print("-" * 60)

    print(
        "Area:",
        test_area
    )

    print(
        "Date:",
        test_date
    )


    features = get_aqi_history_features(
        test_area,
        test_date
    )


    for key, value in features.items():

        print(
            f"{key}: {value}"
        )


    # --------------------------------------------------------
    # Test 2: Future date
    # --------------------------------------------------------

    future_date = "2026-08-28"


    print("\nFuture test")
    print("-" * 60)

    print(
        "Area:",
        test_area
    )

    print(
        "Date:",
        future_date
    )


    future_features = get_aqi_history_features(
        test_area,
        future_date
    )


    for key, value in future_features.items():

        print(
            f"{key}: {value}"
        )


    print("=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)