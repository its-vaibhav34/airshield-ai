import pandas as pd


# ============================================================
# LOAD AQI DATA
# ============================================================

df = pd.read_csv(
    "ml/data/processed/cleaned_punjab_aqi.csv"
)

df["date"] = pd.to_datetime(df["date"])


# ============================================================
# SETTINGS
# ============================================================

area = "Bathinda"

target_date = pd.Timestamp(
    "2025-05-01"
)


# ============================================================
# GET HISTORY BEFORE TARGET DATE
# ============================================================

history = df[
    (df["area"] == area) &
    (df["date"] < target_date)
].copy()

history = (
    history
    .sort_values("date")
    .reset_index(drop=True)
)


# ============================================================
# SHOW RECENT HISTORY
# ============================================================

print("=" * 60)
print("AREA:", area)
print("TARGET DATE:", target_date.date())
print("=" * 60)

print("\nLast 14 observations:")

print(
    history[
        ["date", "aqi_value"]
    ]
    .tail(14)
    .to_string(index=False)
)


# ============================================================
# CALENDAR-DATE LAGS
# ============================================================

indexed = (
    history
    .set_index("date")["aqi_value"]
)

lag_1_date = target_date - pd.Timedelta(days=1)
lag_3_date = target_date - pd.Timedelta(days=3)
lag_7_date = target_date - pd.Timedelta(days=7)


aqi_lag_1d = indexed.get(
    lag_1_date,
    float("nan")
)

aqi_lag_3d = indexed.get(
    lag_3_date,
    float("nan")
)

aqi_lag_7d = indexed.get(
    lag_7_date,
    float("nan")
)


# ============================================================
# ROLLING FEATURES
# ============================================================

aqi_rolling_3d = (
    history["aqi_value"]
    .tail(3)
    .mean()
)

aqi_rolling_7d = (
    history["aqi_value"]
    .tail(7)
    .mean()
)

aqi_rolling_14d = (
    history["aqi_value"]
    .tail(14)
    .mean()
)


# ============================================================
# PRINT FEATURES
# ============================================================

print("\n" + "=" * 60)
print("FUTURE AQI FEATURES")
print("=" * 60)

print("aqi_lag_1d      :", aqi_lag_1d)
print("aqi_lag_3d      :", aqi_lag_3d)
print("aqi_lag_7d      :", aqi_lag_7d)

print("aqi_rolling_3d  :", aqi_rolling_3d)
print("aqi_rolling_7d  :", aqi_rolling_7d)
print("aqi_rolling_14d :", aqi_rolling_14d)