import os
import time

import requests
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT
# ============================================================

load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

API_URL = (
    "https://api.data.gov.in/resource/"
    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
)

API_KEY = os.getenv("DATA_GOV_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "DATA_GOV_API_KEY not found.\n"
        "Make sure .env exists in the project root."
    )


# ============================================================
# PARAMETERS
# ============================================================

params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 10,
    "filters[state]": "Punjab",
    "filters[city]": "Amritsar",
}


# ============================================================
# HEADERS
# ============================================================

headers = {
    "Accept": "application/json",
    "User-Agent": (
        "Mozilla/5.0 "
        "(Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 "
        "(KHTML, like Gecko) "
        "Chrome/151.0 Safari/537.36"
    ),
}


# ============================================================
# API REQUEST WITH RETRIES
# ============================================================

print("=" * 60)
print("CPCB API CONNECTION TEST")
print("=" * 60)

print("Requesting live Amritsar data...")


response = None

for attempt in range(1, 4):

    print(f"Attempt {attempt}/3...")

    try:

        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=(15, 60),
        )

        print(
            "HTTP status:",
            response.status_code
        )

        # Success
        if response.ok:
            break

        # Temporary server errors
        if response.status_code in (
            502,
            503,
            504,
        ):

            if attempt < 3:
                print(
                    "CPCB gateway temporarily unavailable."
                )

                time.sleep(
                    attempt * 3
                )

                continue

        # Other HTTP error
        response.raise_for_status()

    except requests.exceptions.Timeout:

        print(
            "Request timed out."
        )

        if attempt < 3:
            time.sleep(
                attempt * 3
            )
            continue

        raise RuntimeError(
            "CPCB API timed out after 3 attempts."
        )

    except requests.exceptions.RequestException:

        # Never print the exception itself because
        # it may contain the API key in the URL.

        if attempt < 3:
            print(
                "Request failed. Retrying..."
            )

            time.sleep(
                attempt * 3
            )

            continue

        raise RuntimeError(
            "CPCB API request failed."
        )


# ============================================================
# FINAL RESPONSE CHECK
# ============================================================

if response is None:
    raise RuntimeError(
        "No response received from CPCB API."
    )


if not response.ok:

    print(
        "\nCPCB API returned HTTP",
        response.status_code
    )

    print(
        "The API server/gateway is currently "
        "not returning a successful response."
    )

    raise SystemExit(1)


# ============================================================
# PARSE JSON
# ============================================================

try:

    data = response.json()

except ValueError:

    print(
        "\nCPCB API did not return valid JSON."
    )

    print(
        "Response preview:",
        response.text[:500]
    )

    raise SystemExit(1)


# ============================================================
# DISPLAY RESULT
# ============================================================

print()
print("=" * 60)
print("CPCB LIVE DATA")
print("=" * 60)

print(
    "Status:",
    data.get("status")
)

print(
    "Total records:",
    data.get("total")
)

print(
    "Records returned:",
    data.get("count")
)


records = data.get(
    "records",
    []
)


print()
print("Pollutant observations:")
print("-" * 60)


for record in records:

    pollutant = record.get(
        "pollutant_id"
    )

    avg_value = record.get(
        "avg_value"
    )

    min_value = record.get(
        "min_value"
    )

    max_value = record.get(
        "max_value"
    )

    last_update = record.get(
        "last_update"
    )

    print(
        f"{str(pollutant):8s}"
        f" | avg = {avg_value}"
        f" | min = {min_value}"
        f" | max = {max_value}"
        f" | update = {last_update}"
    )


if records:

    print("-" * 60)

    print(
        "Station:",
        records[0].get("station")
    )

    print(
        "City:",
        records[0].get("city")
    )

    print(
        "State:",
        records[0].get("state")
    )


print("=" * 60)
print("CPCB API TEST COMPLETE")
print("=" * 60)