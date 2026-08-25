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


# ============================================================
# KEEP ONLY MODEL AREAS
# ============================================================

fire_df = fire_df[
    fire_df["District"].isin(MODEL_AREAS)
].copy()


# ============================================================
# SORT
# ============================================================

fire_df = (
    fire_df
    .sort_values(["District", "Date"])
    .reset_index(drop=True)
)


# ============================================================
# REMOVE DUPLICATES
# ============================================================

fire_df = (
    fire_df
    .drop_duplicates(
        subset=["District", "Date"],
        keep="last"
    )
    .reset_index(drop=True)
)


# ============================================================
# FIRE COUNT LOOKUP
# ============================================================

fire_lookup = (
    fire_df
    .set_index(["District", "Date"])["fireCount"]
)


# ============================================================
# GET FIRE FEATURE
# ============================================================

def get_fire_feature(
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

        fire_count = fire_lookup.loc[
            (area, target_date)
        ]

    except KeyError:

        raise ValueError(
            f"No fire data available for "
            f"{area} on {target_date.date()}"
        )


    return {
        "fireCount": float(fire_count)
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    test_area = "Amritsar"
    test_date = "2024-01-15"

    feature = get_fire_feature(
        test_area,
        test_date
    )

    print("=" * 60)
    print("FIRE FEATURE")
    print("=" * 60)

    print("Area:", test_area)
    print("Date:", test_date)

    print(
        "fireCount:",
        feature["fireCount"]
    )