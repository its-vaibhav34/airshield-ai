import os
from datetime import datetime

import pandas as pd

from backend.cpcb_service import (
    SUPPORTED_AREAS,
    get_live_cpcb_data,
)


# ============================================================
# PATH
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.dirname(
        os.path.abspath(__file__)
    )
)

HISTORY_DIR = os.path.join(
    BASE_DIR,
    "ml",
    "data",
    "live"
)

HISTORY_PATH = os.path.join(
    HISTORY_DIR,
    "cpcb_aqi_history.csv"
)


# ============================================================
# HISTORY COLUMNS
# ============================================================

HISTORY_COLUMNS = [
    "observed_at",
    "observation_date",
    "collected_at",
    "area",
    "station",
    "aqi",
    "category",
    "last_update",
    "PM2.5",
    "PM10",
    "NO2",
    "SO2",
    "NH3",
    "CO",
    "OZONE",
]


# ============================================================
# LOAD EXISTING HISTORY
# ============================================================

def load_history():

    if not os.path.exists(HISTORY_PATH):

        return pd.DataFrame(
            columns=HISTORY_COLUMNS
        )

    df = pd.read_csv(
        HISTORY_PATH
    )

    # --------------------------------------------------------
    # Ensure expected columns exist.
    # --------------------------------------------------------

    for column in HISTORY_COLUMNS:

        if column not in df.columns:

            df[column] = pd.NA

    return df[
        HISTORY_COLUMNS
    ]


# ============================================================
# SAVE HISTORY
# ============================================================

def save_history(df):

    os.makedirs(
        HISTORY_DIR,
        exist_ok=True
    )

    df.to_csv(
        HISTORY_PATH,
        index=False
    )


# ============================================================
# PARSE CPCB TIMESTAMP
# ============================================================

def parse_cpcb_timestamp(value):

    if value is None:

        return None

    value = str(value).strip()

    if not value:

        return None

    parsed = pd.to_datetime(
        value,
        format="%d-%m-%Y %H:%M:%S",
        errors="coerce"
    )

    if pd.isna(parsed):

        return None

    return parsed.strftime(
        "%Y-%m-%d %H:%M:%S"
    )


# ============================================================
# COLLECT ONE AREA
# ============================================================

def collect_area(area):

    collected_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    live_data = get_live_cpcb_data(
        area
    )

    # --------------------------------------------------------
    # CPCB timestamp
    # --------------------------------------------------------

    cpcb_timestamp = parse_cpcb_timestamp(
        live_data.get("last_update")
    )


    # --------------------------------------------------------
    # Observation timestamp
    #
    # Prefer CPCB timestamp.
    # If CPCB doesn't provide one, use collection time
    # as a fallback.
    # --------------------------------------------------------

    if cpcb_timestamp is not None:

        observed_at = cpcb_timestamp

    else:

        observed_at = collected_at


    # --------------------------------------------------------
    # Observation date
    # --------------------------------------------------------

    observation_date = (
        pd.Timestamp(
            observed_at
        )
        .date()
        .isoformat()
    )


    # --------------------------------------------------------
    # Pollutants are optional.
    #
    # Ludhiana currently has AQI but no pollutant data.
    # --------------------------------------------------------

    pollutants = live_data.get(
        "pollutants",
        {}
    )


    return {

        "observed_at":
            observed_at,

        "observation_date":
            observation_date,

        "collected_at":
            collected_at,

        "area":
            live_data["area"],

        "station":
            live_data["station"],

        "aqi":
            live_data["aqi"],

        "category":
            live_data["category"],

        "last_update":
            cpcb_timestamp,

        "PM2.5":
            pollutants.get("PM2.5"),

        "PM10":
            pollutants.get("PM10"),

        "NO2":
            pollutants.get("NO2"),

        "SO2":
            pollutants.get("SO2"),

        "NH3":
            pollutants.get("NH3"),

        "CO":
            pollutants.get("CO"),

        "OZONE":
            pollutants.get("OZONE"),
    }


# ============================================================
# COLLECT ALL AREAS
# ============================================================

def collect_all_areas():

    history = load_history()

    new_rows = []


    print("=" * 65)
    print("CPCB HISTORY COLLECTION")
    print("=" * 65)


    # ========================================================
    # COLLECT
    # ========================================================

    for area in sorted(
        SUPPORTED_AREAS
    ):

        print(
            f"\nCollecting: {area}"
        )

        try:

            row = collect_area(
                area
            )

            new_rows.append(
                row
            )


            print(
                f"  AQI        : {row['aqi']}"
            )

            print(
                f"  Station    : {row['station']}"
            )

            print(
                f"  CPCB update: "
                f"{row['last_update']}"
            )

            print(
                f"  Observed at: "
                f"{row['observed_at']}"
            )


            # ------------------------------------------------
            # Check pollutant availability
            # ------------------------------------------------

            pollutant_columns = [
                "PM2.5",
                "PM10",
                "NO2",
                "SO2",
                "NH3",
                "CO",
                "OZONE",
            ]

            available_pollutants = [
                column
                for column in pollutant_columns
                if pd.notna(
                    row.get(column)
                )
            ]


            if available_pollutants:

                print(
                    "  Pollutants : available"
                )

            else:

                print(
                    "  Pollutants : unavailable"
                )


        except Exception as e:

            print(
                f"  ERROR: {e}"
            )


    # ========================================================
    # NOTHING COLLECTED
    # ========================================================

    if not new_rows:

        print(
            "\nNo CPCB observations collected."
        )

        return


    new_df = pd.DataFrame(
        new_rows,
        columns=HISTORY_COLUMNS
    )


    # ========================================================
    # COMBINE OLD + NEW
    # ========================================================

    history = pd.concat(
        [
            history,
            new_df
        ],
        ignore_index=True
    )


    # ========================================================
    # NORMALIZE TIMESTAMPS
    # ========================================================

    history["observed_at"] = pd.to_datetime(
        history["observed_at"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    history["collected_at"] = pd.to_datetime(
        history["collected_at"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )

    history["last_update"] = pd.to_datetime(
        history["last_update"],
        format="%Y-%m-%d %H:%M:%S",
        errors="coerce"
    )


    # ========================================================
    # REBUILD OBSERVATION DATE
    # ========================================================

    history["observation_date"] = (
        history["observed_at"]
        .dt
        .date
        .astype(str)
    )


    # ========================================================
    # DUPLICATE HANDLING
    #
    # We maintain ONE AQI observation per:
    #
    #     area + observation_date
    #
    # If multiple records exist for the same day:
    #
    #     CPCB timestamp available
    #             ↓
    #         preferred
    #
    #     fallback timestamp
    #             ↓
    #         lower priority
    #
    # If both are available, keep the CPCB-timestamped row.
    # ========================================================

    history["_has_cpcb_timestamp"] = (
        history["last_update"].notna()
    )


    history = (
        history
        .sort_values(
            [
                "area",
                "observation_date",
                "_has_cpcb_timestamp",
                "collected_at",
            ]
        )
        .drop_duplicates(
            subset=[
                "area",
                "observation_date",
            ],
            keep="last"
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # REMOVE INTERNAL COLUMN
    # ========================================================

    history = history.drop(
        columns=[
            "_has_cpcb_timestamp"
        ]
    )


    # ========================================================
    # SORT FINAL HISTORY
    # ========================================================

    history = (
        history
        .sort_values(
            [
                "area",
                "observed_at"
            ]
        )
        .reset_index(
            drop=True
        )
    )


    # ========================================================
    # CONVERT TIMESTAMPS TO CSV STRINGS
    # ========================================================

    history["observed_at"] = (
        history["observed_at"]
        .dt
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    history["collected_at"] = (
        history["collected_at"]
        .dt
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    history["last_update"] = (
        history["last_update"]
        .dt
        .strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )


    # ========================================================
    # SAVE
    # ========================================================

    save_history(
        history
    )


    # ========================================================
    # SUMMARY
    # ========================================================

    print("\n" + "=" * 65)
    print("COLLECTION COMPLETE")
    print("=" * 65)

    print(
        "History file:",
        HISTORY_PATH
    )

    print(
        "Total observations:",
        len(history)
    )

    print(
        "Areas:",
        history["area"].nunique()
    )

    print("=" * 65)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    collect_all_areas()