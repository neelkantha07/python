import swisseph as swe
from datetime import datetime, timedelta
import pandas as pd

# Set location for Mumbai
LAT = 19.0760
LON = 72.8777
TZ_OFFSET = 5.5  # IST (India Standard Time)

# KP Nakshatra lords (27 nakshatras)
nakshatra_lords = ['Ketu', 'Venus', 'Sun', 'Moon', 'Mars', 'Rahu',
                   'Jupiter', 'Saturn', 'Mercury'] * 3

# Vimshottari dasha balance
dasha_years = {
    'Ketu': 7, 'Venus': 20, 'Sun': 6, 'Moon': 10, 'Mars': 7,
    'Rahu': 18, 'Jupiter': 16, 'Saturn': 19, 'Mercury': 17
}
total_dasha = sum(dasha_years.values())  # 120 years

# Constants
nakshatra_span = 13 + 20/60  # 13.333... deg

# Setup Swiss Ephemeris
swe.set_ephe_path('.')  # Set path to where ephemeris files are stored
swe.set_sid_mode(swe.SIDM_LAHIRI)  # Lahiri = JHora default
swe.set_topo(LON, LAT, 0)

# Function to get KP details
def get_kp_details(moon_longitude):
    nak_num = int(moon_longitude // nakshatra_span) + 1
    nak_lord = nakshatra_lords[nak_num - 1]
    start_deg = (nak_num - 1) * nakshatra_span
    degrees_in_nak = moon_longitude - start_deg

    # Sublord calculation
    sub_lord = None
    elapsed = 0.0
    for lord, years in dasha_years.items():
        portion = (years / total_dasha) * nakshatra_span
        if degrees_in_nak < elapsed + portion:
            sub_lord = lord
            break
        elapsed += portion

    return nak_num, nak_lord, sub_lord

# Function to track changes
def find_moon_sublord_transits(start_dt, end_dt, step_min=1):
    records = []
    last_sub = None
    current_dt = start_dt

    while current_dt <= end_dt:
        utc_dt = current_dt - timedelta(hours=TZ_OFFSET)
        jd = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute / 60.0)

        moon = swe.calc_ut(jd, swe.MOON)[0][0]  # sidereal due to sid_mode

        nak_num, nak_lord, sub_lord = get_kp_details(moon)

        if sub_lord != last_sub:
            records.append({
                'Time (IST)': current_dt.strftime('%Y-%m-%d %H:%M'),
                'Moon Longitude': round(moon, 4),
                'Nakshatra No': nak_num,
                'Nakshatra Lord': nak_lord,
                'Sublord': sub_lord
            })
            last_sub = sub_lord

        current_dt += timedelta(minutes=step_min)

    return pd.DataFrame(records)

# Define start/end
start = datetime(2025, 5, 2, 0, 0)
end = datetime(2025, 5, 18, 0, 0)

# Run
df = find_moon_sublord_transits(start, end, step_min=2)
df.to_csv("moon_sublord_kp_mumbai.csv", index=False)
print("Saved moon_sublord_kp_mumbai.csv")
