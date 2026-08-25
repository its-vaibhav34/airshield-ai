import pandas as pd


STATIONS_URL = (
    "https://raw.githubusercontent.com/"
    "deepanshu88/Datasets/master/UploadedFiles/stations.csv"
)

AREAS = [
    "Amritsar",
    "Bathinda",
    "Jalandhar",
    "Ludhiana",
    "Patiala",
    "Rupnagar",
]


print("=" * 70)
print("CPCB STATION AQI CHECK")
print("=" * 70)


stations = pd.read_csv(STATIONS_URL)


print("Total stations:", len(stations))
print()


for area in AREAS:

    matches = stations[
        stations["cityID"].astype(str).str.lower()
        == area.lower()
    ].copy()

    print("-" * 70)
    print("AREA:", area)

    if matches.empty:

        print("NO STATION FOUND")
        continue

    print(
        matches[
            [
                "id",
                "stationID",
                "live",
                "avg",
                "cityID",
                "stateID",
            ]
        ].to_string(index=False)
    )


print()
print("=" * 70)
print("TEST COMPLETE")
print("=" * 70)