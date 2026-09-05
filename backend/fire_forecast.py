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

FIRE_PATH = os.path.join(
    BASE_DIR,
    "ml",
    "data",
    "processed",
    "cleaned_fire.csv"
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
# LOAD FIRE DATA
# ============================================================

fire_df = pd.read_csv(FIRE_PATH)

fire_df["Date"] = pd.to_datetime(
    fire_df["Date"]
)

fire_df = fire_df[
    fire_df["District"].isin(MODEL_AREAS)
].copy()


# ============================================================
# FUTURE FIRE ESTIMATION
# ============================================================

def get_future_fire_feature(
    area: str,
    target_date
):

    if area not in MODEL_AREAS:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {MODEL_AREAS}"
        )


    target_date = pd.Timestamp(
        target_date
    )

    target_month = target_date.month


    # --------------------------------------------------------
    # Historical observations for same area + month
    # --------------------------------------------------------

    historical = fire_df[
        (fire_df["District"] == area)
        &
        (fire_df["Date"].dt.month == target_month)
    ].copy()


    if historical.empty:

        raise ValueError(
            f"No historical fire data available "
            f"for {area} in month {target_month}"
        )


    # --------------------------------------------------------
    # Expected fire count
    #
    # Mean of historical same-month observations.
    # --------------------------------------------------------

    expected_fire_count = (
        historical["fireCount"]
        .mean()
    )


    # --------------------------------------------------------
    # Return model-compatible feature
    # --------------------------------------------------------

    return {
        "fireCount": float(
            expected_fire_count
        )
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_area = "Amritsar"
    test_date = "2026-08-26"

    print("=" * 65)
    print("AIRSHIELD FUTURE FIRE TEST")
    print("=" * 65)

    print("Area:", test_area)
    print("Date:", test_date)

    feature = get_future_fire_feature(
        test_area,
        test_date
    )

    print(
        "\nExpected future fireCount:",
        feature["fireCount"]
    )

    print("-" * 65)
    print("TEST COMPLETE")
    print("=" * 65)