"""
CPCB National AQI Calculator

Converts pollutant concentrations into an overall AQI
using CPCB National Air Quality Index breakpoints.
"""

import math


# ============================================================
# CPCB AQI BREAKPOINTS
# ============================================================
#
# Each tuple:
# (concentration_low, concentration_high,
#  AQI_low, AQI_high)
#
# Based on CPCB National AQI methodology.
# ============================================================

BREAKPOINTS = {

    "PM10": [
        (0, 50, 0, 50),
        (51, 100, 51, 100),
        (101, 250, 101, 200),
        (251, 350, 201, 300),
        (351, 430, 301, 400),
        (430, float("inf"), 401, 500),
    ],

    "PM2.5": [
        (0, 30, 0, 50),
        (31, 60, 51, 100),
        (61, 90, 101, 200),
        (91, 120, 201, 300),
        (121, 250, 301, 400),
        (250, float("inf"), 401, 500),
    ],

    "NO2": [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 180, 101, 200),
        (181, 280, 201, 300),
        (281, 400, 301, 400),
        (400, float("inf"), 401, 500),
    ],

    "O3": [
        (0, 50, 0, 50),
        (51, 80, 51, 100),
        (81, 180, 101, 200),
        (181, 280, 201, 300),
        (281, 400, 301, 400),
        (400, float("inf"), 401, 500),
    ],

    "CO": [
        (0, 1.0, 0, 50),
        (1.1, 2.0, 51, 100),
        (2.1, 10.0, 101, 200),
        (10.1, 17.0, 201, 300),
        (17.1, 34.0, 301, 400),
        (34.0, float("inf"), 401, 500),
    ],

    "SO2": [
        (0, 40, 0, 50),
        (41, 80, 51, 100),
        (81, 380, 101, 200),
        (381, 800, 201, 300),
        (801, 1600, 301, 400),
        (1600, float("inf"), 401, 500),
    ],

    "NH3": [
        (0, 200, 0, 50),
        (201, 400, 51, 100),
        (401, 800, 101, 200),
        (801, 1200, 201, 300),
        (1201, 1800, 301, 400),
        (1800, float("inf"), 401, 500),
    ],
}


# ============================================================
# AQI CATEGORY
# ============================================================

def get_aqi_category(aqi):
    """
    Convert numeric AQI into CPCB category.
    """

    if aqi <= 50:
        return "Good"

    if aqi <= 100:
        return "Satisfactory"

    if aqi <= 200:
        return "Moderate"

    if aqi <= 300:
        return "Poor"

    if aqi <= 400:
        return "Very Poor"

    return "Severe"


# ============================================================
# POLLUTANT SUB-INDEX
# ============================================================

def calculate_sub_index(pollutant, concentration):
    """
    Calculate AQI sub-index for one pollutant
    using linear interpolation.
    """

    if concentration is None:
        return None

    try:
        concentration = float(concentration)
    except (TypeError, ValueError):
        return None

    if math.isnan(concentration):
        return None

    if concentration < 0:
        return None

    if pollutant not in BREAKPOINTS:
        return None

    for (
        concentration_low,
        concentration_high,
        aqi_low,
        aqi_high,
    ) in BREAKPOINTS[pollutant]:

        if concentration <= concentration_high:

            # Avoid division by zero
            if concentration_high == concentration_low:
                return float(aqi_low)

            aqi = (
                (
                    (aqi_high - aqi_low)
                    /
                    (concentration_high - concentration_low)
                )
                *
                (concentration - concentration_low)
                +
                aqi_low
            )

            return round(aqi, 2)

    return 500.0


# ============================================================
# OVERALL AQI
# ============================================================

def calculate_aqi(pollutants):
    """
    Calculate overall AQI from pollutant concentrations.

    Parameters
    ----------
    pollutants : dict

        Example:

        {
            "PM2.5": 69,
            "PM10": 86,
            "SO2": 16,
            "NO2": 16,
            "NH3": 5,
            "CO": 0.026,
            "O3": 11
        }

    Returns
    -------
    dict
        {
            "aqi": ...,
            "category": ...,
            "dominant_pollutant": ...,
            "sub_indices": {...}
        }
    """

    sub_indices = {}

    for pollutant, concentration in pollutants.items():

        sub_index = calculate_sub_index(
            pollutant,
            concentration
        )

        if sub_index is not None:
            sub_indices[pollutant] = sub_index

    if not sub_indices:
        raise ValueError(
            "No valid pollutant data available for AQI calculation."
        )

    dominant_pollutant = max(
        sub_indices,
        key=sub_indices.get
    )

    overall_aqi = sub_indices[dominant_pollutant]

    return {
        "aqi": round(overall_aqi, 2),
        "category": get_aqi_category(overall_aqi),
        "dominant_pollutant": dominant_pollutant,
        "sub_indices": sub_indices,
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    sample_pollutants = {
        "PM2.5": 69,
        "PM10": 86,
        "SO2": 16,
        "NO2": 16,
        "NH3": 5,
        "CO": 0.026,
        "O3": 11,
    }

    result = calculate_aqi(
        sample_pollutants
    )

    print("=" * 60)
    print("CPCB AQI CALCULATOR TEST")
    print("=" * 60)

    print("Overall AQI      :", result["aqi"])
    print("Category         :", result["category"])
    print(
        "Dominant pollutant:",
        result["dominant_pollutant"]
    )

    print("\nSub-indices:")

    for pollutant, value in result["sub_indices"].items():
        print(
            f"{pollutant:8s}: {value}"
        )