import os
import requests
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CPCB CONFIGURATION
# ============================================================

CPCB_API_URL = (
    "https://api.data.gov.in/resource/"
    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
)

CPCB_API_KEY = os.getenv("DATA_GOV_API_KEY")


# ============================================================
# SUPPORTED AREAS
# ============================================================

SUPPORTED_AREAS = [
    "Amritsar",
    "Bathinda",
    "Jalandhar",
    "Ludhiana",
    "Patiala",
    "Rupnagar",
]


# ============================================================
# GET LIVE CPCB DATA
# ============================================================

def get_live_cpcb_data(area: str) -> dict:

    # --------------------------------------------------------
    # Validate area
    # --------------------------------------------------------

    if area not in SUPPORTED_AREAS:
        raise ValueError(
            f"Area '{area}' is not supported. "
            f"Supported areas: {SUPPORTED_AREAS}"
        )

    # --------------------------------------------------------
    # Validate API key
    # --------------------------------------------------------

    if not CPCB_API_KEY:
        raise RuntimeError(
            "DATA_GOV_API_KEY is not configured."
        )

    # --------------------------------------------------------
    # API parameters
    # --------------------------------------------------------

    params = {
        "api-key": CPCB_API_KEY,
        "format": "json",
        "limit": 100,
        "filters[state]": "Punjab",
        "filters[city]": area,
    }

    # --------------------------------------------------------
    # Request headers
    # --------------------------------------------------------

    headers = {
        "Accept": "application/json",
        "User-Agent": "AirShield-AI/1.0",
    }

    # --------------------------------------------------------
    # API request
    # --------------------------------------------------------

    try:

        response = requests.get(
            CPCB_API_URL,
            params=params,
            headers=headers,
            timeout=(15, 60),
        )

    except requests.exceptions.Timeout:

        raise RuntimeError(
            "CPCB API request timed out."
        )

    except requests.exceptions.RequestException:

        raise RuntimeError(
            "Unable to connect to CPCB API."
        )

    # --------------------------------------------------------
    # HTTP status
    # --------------------------------------------------------

    if not response.ok:

        raise RuntimeError(
            f"CPCB API returned HTTP "
            f"{response.status_code}"
        )

    # --------------------------------------------------------
    # JSON parsing
    # --------------------------------------------------------

    try:

        data = response.json()

    except ValueError:

        raise RuntimeError(
            "CPCB API returned invalid JSON."
        )

    # --------------------------------------------------------
    # Records
    # --------------------------------------------------------

    records = data.get("records", [])

    if not records:

        raise RuntimeError(
            f"No live CPCB data available for {area}."
        )

    # --------------------------------------------------------
    # Convert records into clean structure
    # --------------------------------------------------------

    pollutants = {}

    station = None
    last_update = None

    for record in records:

        pollutant = record.get("pollutant_id")

        if not pollutant:
            continue

        try:

            avg_value = float(
                record.get("avg_value")
            )

        except (TypeError, ValueError):

            continue

        pollutants[pollutant] = avg_value

        if station is None:
            station = record.get("station")

        if last_update is None:
            last_update = record.get("last_update")

    # --------------------------------------------------------
    # Final response
    # --------------------------------------------------------

    return {
        "area": area,
        "station": station,
        "last_update": last_update,
        "pollutants": pollutants,
    }