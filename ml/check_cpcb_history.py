import os
import requests
from dotenv import load_dotenv


# ============================================================
# ENVIRONMENT
# ============================================================

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


# ============================================================
# CONFIG
# ============================================================

AREA = "Amritsar"

OFFSETS = [
    0,
    10,
    20,
    50,
    100,
    200,
    500,
]


# ============================================================
# HEADERS
# ============================================================

headers = {
    "Accept": "application/json",
    "User-Agent": "AirShield-AI/1.0",
}


# ============================================================
# TEST
# ============================================================

print("=" * 70)
print("CPCB PAGINATION / HISTORY TEST")
print("=" * 70)

print("Area:", AREA)
print()


all_records = []


for offset in OFFSETS:

    print("-" * 70)
    print(f"Requesting offset={offset}, limit=10")

    params = {
        "api-key": API_KEY,
        "format": "json",
        "offset": offset,
        "limit": 10,
        "filters[state]": "Punjab",
        "filters[city]": AREA,
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            headers=headers,
            timeout=(15, 60),
        )

    except requests.exceptions.RequestException as e:

        print("REQUEST ERROR:")
        print(e)
        continue


    print("HTTP status:", response.status_code)

    if not response.ok:

        print(
            "ERROR:",
            response.status_code,
            response.text[:300]
        )

        continue


    try:

        data = response.json()

    except ValueError:

        print("ERROR: Invalid JSON")
        continue


    records = data.get("records", [])

    print("Total available:", data.get("total"))
    print("Returned:", len(records))


    if not records:

        print("No records returned.")

        continue


    # --------------------------------------------------------
    # Print records from this page
    # --------------------------------------------------------

    for record in records:

        timestamp = record.get("last_update")
        station = record.get("station")
        pollutant = record.get("pollutant_id")
        avg_value = record.get("avg_value")

        print(
            f"{timestamp} | "
            f"{pollutant:<7} | "
            f"avg={avg_value} | "
            f"{station}"
        )

        all_records.append(record)


# ============================================================
# UNIQUE TIMESTAMPS
# ============================================================

print()
print("=" * 70)
print("ALL UNIQUE TIMESTAMPS FOUND")
print("=" * 70)

timestamps = sorted(
    set(
        record.get("last_update")
        for record in all_records
        if record.get("last_update")
    )
)

for timestamp in timestamps:
    print(timestamp)


# ============================================================
# UNIQUE STATIONS
# ============================================================

print()
print("=" * 70)
print("STATIONS")
print("=" * 70)

stations = sorted(
    set(
        record.get("station")
        for record in all_records
        if record.get("station")
    )
)

for station in stations:
    print(station)


# ============================================================
# UNIQUE POLLUTANTS
# ============================================================

print()
print("=" * 70)
print("POLLUTANTS")
print("=" * 70)

pollutants = sorted(
    set(
        record.get("pollutant_id")
        for record in all_records
        if record.get("pollutant_id")
    )
)

for pollutant in pollutants:
    print(pollutant)


# ============================================================
# SUMMARY
# ============================================================

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)

print("Pages requested:", len(OFFSETS))
print("Total records collected:", len(all_records))
print("Unique timestamps:", len(timestamps))

if len(timestamps) > 1:

    print()
    print("SUCCESS:")
    print("Historical/multiple timestamp data is accessible.")

else:

    print()
    print("IMPORTANT:")
    print("Only one timestamp was found.")
    print("Pagination did not expose historical observations.")


print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)