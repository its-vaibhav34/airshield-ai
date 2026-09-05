import os
from functools import lru_cache

import pandas as pd
import requests
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CONFIG
# ============================================================

DATA_GOV_API_URL = (
    "https://api.data.gov.in/resource/"
    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
)

STATIONS_URL = (
    "https://raw.githubusercontent.com/"
    "deepanshu88/Datasets/master/UploadedFiles/stations.csv"
)

API_KEY = os.getenv("DATA_GOV_API_KEY")


# ============================================================
# SUPPORTED AREAS
# ============================================================

SUPPORTED_AREAS = {
    "Amritsar",
    "Bathinda",
    "Jalandhar",
    "Ludhiana",
    "Patiala",
    "Rupnagar",
}


# ============================================================
# HEADERS
# ============================================================

HEADERS = {
    "Accept": "application/json",
    "User-Agent": "AirShield-AI/1.0",
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
# LOAD STATION DATA
# ============================================================

@lru_cache(maxsize=1)
def get_station_data():

    try:

        df = pd.read_csv(
            STATIONS_URL
        )

    except Exception as e:

        raise ValueError(
            f"Unable to load CPCB station data: {e}"
        )

    required_columns = {
        "id",
        "stationID",
        "live",
        "avg",
        "cityID",
        "stateID",
    }

    missing = required_columns - set(
        df.columns
    )

    if missing:

        raise ValueError(
            f"CPCB station data missing columns: {sorted(missing)}"
        )

    return df


# ============================================================
# GET CPCB STATION / AQI
# ============================================================

def get_station_aqi(area: str):

    df = get_station_data()

    matches = df[
        (df["cityID"].astype(str).str.lower() == area.lower())
        &
        (df["stateID"].astype(str).str.lower() == "punjab")
    ].copy()

    if matches.empty:

        raise ValueError(
            f"No CPCB station found for {area}"
        )

    # Prefer a currently live station.
    live_matches = matches[
        matches["live"].astype(str).str.lower() == "true"
    ]

    if not live_matches.empty:

        matches = live_matches

    row = matches.iloc[0]

    station = str(
        row["stationID"]
    )

    try:

        aqi = float(
            row["avg"]
        )

    except (TypeError, ValueError):

        raise ValueError(
            f"Invalid AQI value received for {area}"
        )

    return {
        "station": station,
        "aqi": aqi,
        "category": get_aqi_category(aqi),
    }


# ============================================================
# GET LIVE POLLUTANTS
# ============================================================

def get_live_pollutants(area: str):

    if not API_KEY:

        raise ValueError(
            "DATA_GOV_API_KEY not found in .env"
        )

    params = {
        "api-key": API_KEY,
        "format": "json",
        "limit": 10,
        "filters[state]": "Punjab",
        "filters[city]": area,
    }

    try:

        response = requests.get(
            DATA_GOV_API_URL,
            params=params,
            headers=HEADERS,
            timeout=(15, 60),
        )

    except requests.exceptions.RequestException as e:

        raise ValueError(
            f"CPCB live data request failed: {e}"
        )

    if not response.ok:

        raise ValueError(
            f"CPCB live data API returned HTTP {response.status_code}"
        )

    try:

        data = response.json()

    except ValueError:

        raise ValueError(
            "CPCB live data API returned invalid JSON"
        )

    records = data.get(
        "records",
        []
    )

    if not records:

        raise ValueError(
            f"No live CPCB pollutant data available for {area}"
        )

    pollutants = {}

    station = None
    last_update = None

    for record in records:

        pollutant_id = record.get(
            "pollutant_id"
        )

        avg_value = record.get(
            "avg_value"
        )

        if pollutant_id is None:
            continue

        try:

            pollutants[pollutant_id] = float(
                avg_value
            )

        except (TypeError, ValueError):

            continue

        if station is None:

            station = record.get(
                "station"
            )

        if last_update is None:

            last_update = record.get(
                "last_update"
            )

    if not pollutants:

        raise ValueError(
            f"No valid pollutant values available for {area}"
        )

    return {
        "station": station,
        "last_update": last_update,
        "pollutants": pollutants,
    }


# ============================================================
# COMBINED LIVE CPCB DATA
# ============================================================

def get_live_cpcb_data(area: str):

    if area not in SUPPORTED_AREAS:

        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {sorted(SUPPORTED_AREAS)}"
        )

    # --------------------------------------------------------
    # Current AQI from CPCB station data
    # --------------------------------------------------------

    station_data = get_station_aqi(
        area
    )

    # --------------------------------------------------------
    # Current pollutant observations
    # --------------------------------------------------------

    try:
        pollutant_data = get_live_pollutants(
            area
        )

    except ValueError:
        pollutant_data = {
            "station": None,
            "last_update": None,
            "pollutants": {}
        }

    # --------------------------------------------------------
    # Prefer station name from pollutant API when available
    # --------------------------------------------------------

    station = (
        pollutant_data["station"]
        or station_data["station"]
    )

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {

        "area": area,

        "station": station,

        "aqi": round(
            station_data["aqi"],
            2
        ),

        "category": station_data["category"],

        "last_update":
            pollutant_data["last_update"],

        "pollutants":
            pollutant_data["pollutants"],
    }
