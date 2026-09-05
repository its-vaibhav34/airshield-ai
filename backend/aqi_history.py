import os

import pandas as pd


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)


HISTORICAL_AQI_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "data",
    "processed",
    "cleaned_punjab_aqi.csv"
)


LIVE_AQI_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "data",
    "live",
    "cpcb_aqi_history.csv"
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
    "Rupnagar",
]


# ============================================================
# LOAD HISTORICAL AQI
# ============================================================

def load_historical_aqi():

    if not os.path.exists(
        HISTORICAL_AQI_PATH
    ):

        raise ValueError(
            "Historical AQI file not found: "
            f"{HISTORICAL_AQI_PATH}"
        )


    df = pd.read_csv(
        HISTORICAL_AQI_PATH
    )


    required_columns = {
        "date",
        "area",
        "aqi_value",
    }


    missing = (
        required_columns
        - set(df.columns)
    )


    if missing:

        raise ValueError(
            "Historical AQI file is missing "
            f"columns: {sorted(missing)}"
        )


    df = df[
        [
            "date",
            "area",
            "aqi_value",
        ]
    ].copy()


    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )


    df["aqi_value"] = pd.to_numeric(
        df["aqi_value"],
        errors="coerce"
    )


    df = df.dropna(
        subset=[
            "date",
            "area",
            "aqi_value",
        ]
    )


    df = df[
        df["area"].isin(
            MODEL_AREAS
        )
    ].copy()


    return df


# ============================================================
# LOAD LIVE CPCB AQI HISTORY
# ============================================================

def load_live_aqi():

    if not os.path.exists(
        LIVE_AQI_PATH
    ):

        return pd.DataFrame(
            columns=[
                "date",
                "area",
                "aqi_value",
            ]
        )


    df = pd.read_csv(
        LIVE_AQI_PATH
    )


    required_columns = {
        "observation_date",
        "area",
        "aqi",
    }


    missing = (
        required_columns
        - set(df.columns)
    )


    if missing:

        raise ValueError(
            "CPCB history file is missing "
            f"columns: {sorted(missing)}"
        )


    df = df[
        [
            "observation_date",
            "area",
            "aqi",
        ]
    ].copy()


    df = df.rename(
        columns={
            "observation_date": "date",
            "aqi": "aqi_value",
        }
    )


    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )


    df["aqi_value"] = pd.to_numeric(
        df["aqi_value"],
        errors="coerce"
    )


    df = df.dropna(
        subset=[
            "date",
            "area",
            "aqi_value",
        ]
    )


    df = df[
        df["area"].isin(
            MODEL_AREAS
        )
    ].copy()


    return df


# ============================================================
# GET UNIFIED AQI HISTORY
# ============================================================

def get_aqi_history():

    historical = load_historical_aqi()

    live = load_live_aqi()


    # --------------------------------------------------------
    # Combine historical + CPCB live history
    # --------------------------------------------------------

    combined = pd.concat(
        [
            historical,
            live,
        ],
        ignore_index=True
    )


    # --------------------------------------------------------
    # Sort
    # --------------------------------------------------------

    combined = (
        combined
        .sort_values(
            [
                "area",
                "date",
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # --------------------------------------------------------
    # Remove duplicate area/date
    #
    # If CPCB live data overlaps with historical data,
    # the later row (live data) wins.
    # --------------------------------------------------------

    combined = (
        combined
        .drop_duplicates(
            subset=[
                "area",
                "date",
            ],
            keep="last"
        )
        .reset_index(
            drop=True
        )
    )


    return combined


# ============================================================
# GET AREA HISTORY BEFORE TARGET DATE
# ============================================================

def get_area_history(
    area: str,
    target_date,
):

    if area not in MODEL_AREAS:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {MODEL_AREAS}"
        )


    target_date = pd.Timestamp(
        target_date
    )


    history = get_aqi_history()


    area_history = history[
        (history["area"] == area)
        &
        (history["date"] < target_date)
    ].copy()


    area_history = (
        area_history
        .sort_values("date")
        .reset_index(drop=True)
    )


    if area_history.empty:

        raise ValueError(
            f"No AQI history available for "
            f"{area} before "
            f"{target_date.date()}"
        )


    return area_history


# ============================================================
# GET LATEST KNOWN AQI
# ============================================================

def get_latest_aqi(
    area: str,
    before_date=None,
):

    if area not in MODEL_AREAS:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {MODEL_AREAS}"
        )


    history = get_aqi_history()


    area_history = history[
        history["area"] == area
    ].copy()


    if before_date is not None:

        before_date = pd.Timestamp(
            before_date
        )

        area_history = area_history[
            area_history["date"] < before_date
        ]


    if area_history.empty:

        raise ValueError(
            f"No AQI history available for "
            f"{area}"
        )


    row = (
        area_history
        .sort_values("date")
        .iloc[-1]
    )


    return {
        "date": row["date"].date().isoformat(),
        "aqi": float(row["aqi_value"]),
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print("=" * 65)
    print("AIRSHIELD UNIFIED AQI HISTORY TEST")
    print("=" * 65)


    # --------------------------------------------------------
    # Load combined history
    # --------------------------------------------------------

    history = get_aqi_history()


    print(
        "\nTotal unified observations:",
        len(history)
    )


    print(
        "Areas:",
        history["area"].nunique()
    )


    # --------------------------------------------------------
    # Show latest AQI for every area
    # --------------------------------------------------------

    print("\nLatest known AQI:")
    print("-" * 65)


    for area in MODEL_AREAS:

        try:

            latest = get_latest_aqi(
                area
            )

            print(
                f"{area:<12} "
                f"{latest['date']} "
                f"→ AQI {latest['aqi']}"
            )

        except ValueError as e:

            print(
                f"{area:<12} ERROR: {e}"
            )


    # --------------------------------------------------------
    # Test future date
    # --------------------------------------------------------

    test_area = "Amritsar"

    test_date = "2026-08-28"


    print("\nFuture-date history test:")
    print("-" * 65)

    print(
        "Area:",
        test_area
    )

    print(
        "Target date:",
        test_date
    )


    area_history = get_area_history(
        test_area,
        test_date
    )


    print(
        "Latest AQI before target:",
        area_history.iloc[-1]["aqi_value"]
    )

    print(
        "Latest date before target:",
        area_history.iloc[-1]["date"].date()
    )


    print("=" * 65)
    print("TEST COMPLETE")
    print("=" * 65)