import os
import requests
from dotenv import load_dotenv


load_dotenv()


API_URL = (
    "https://api.data.gov.in/resource/"
    "3b01bcb8-0b14-4abf-b6f2-c1bfd384ba69"
)

API_KEY = os.getenv("DATA_GOV_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "DATA_GOV_API_KEY not found in .env"
    )


params = {
    "api-key": API_KEY,
    "format": "json",
    "limit": 100,

    "filters[state]": "Punjab",
    "filters[city]": "Amritsar",
}


headers = {
    "Accept": "application/json",
    "User-Agent": "AirShield-AI/1.0",
}


print("=" * 60)
print("CPCB HISTORY TEST")
print("=" * 60)

try:

    response = requests.get(
        API_URL,
        params=params,
        headers=headers,
        timeout=(15, 60),
    )

except requests.exceptions.RequestException:
    print("CPCB API request failed.")
    raise SystemExit(1)


print("HTTP status:", response.status_code)


if not response.ok:

    print(
        "CPCB API returned:",
        response.status_code
    )

    raise SystemExit(1)


data = response.json()

records = data.get("records", [])


print("Total records:", data.get("total"))
print("Returned:", len(records))


print("\nUnique timestamps:")

timestamps = sorted(
    set(
        record.get("last_update")
        for record in records
    )
)

for timestamp in timestamps:
    print(timestamp)


print("\nStations:")

stations = sorted(
    set(
        record.get("station")
        for record in records
    )
)

for station in stations:
    print(station)


print("\nPollutants:")

pollutants = sorted(
    set(
        record.get("pollutant_id")
        for record in records
    )
)

for pollutant in pollutants:
    print(pollutant)


print("=" * 60)
print("TEST COMPLETE")
print("=" * 60)