# Appy.py
import requests
import json
from skyfield.api import load, EarthSatellite
import numpy as np
from db import TLEDatabase 
from Collision_Detector import CollisionDetector
from datetime import datetime, timedelta, timezone
import streamlit as st
import pandas as pd
import logging
import matplotlib.pyplot as plt

"""
Collision tracker
    - Call API Get TLE of 2 elements (http://tle.ivanstanojevic.me/api/tle)
    - 
"""
# API doesn't check value of User-Agent
HEADERS = {
    "User-Agent": "xxxx",
    "Accept": "application/json"
    }
CURR_TIME = current_utc = datetime.now(timezone.utc)

# Streamlit
st.title("Satellite Collision Detector 🚀")
st.write(f"**Current UTC Time:** {CURR_TIME.strftime('%Y-%m-%d %H:%M:%S')}")
tab1, tab2 = st.tabs(["Overview", "Run Detection"])

# Logging 
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log"),   
        logging.StreamHandler()
    ]
)

# Example usage
logging.info("App started")

db = TLEDatabase()
cd = CollisionDetector(6, db)
tles = None

# Get satellites TLEs
try:
    # Don't fetch TLEs if it's less than 1 hour old
    last_update = db.get_last_updated()
    if last_update:
        last_update = datetime.fromisoformat(last_update)
    else:
        last_update = None
    threshold = timedelta(hours=1)
    if last_update:
        st.write(f"**Last Database Update:** {last_update}")

    if last_update == None or CURR_TIME - last_update >= threshold:
        response = requests.get("http://tle.ivanstanojevic.me/api/tle", headers=HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        tles = response.json()['member']
except requests.exceptions.RequestException as e:
    logging.error(f"Error fetching TLE data: {e}")

logging.info(f"TLEs: {tles}")
if tles:
    for i, tle1 in enumerate(tles):
        es1 = EarthSatellite(tle1['line1'], tle1['line2'], str(tle1['name']))
        db.insert_or_update_tle(
            tle1['satelliteId'],
            tle1['name'],
            tle1['line1'],
            tle1['line2'],
            tle1['date']
        )
        j = i + 1
        while j < len(tles):
            tle2 = tles[j]
            es2 = EarthSatellite(tle2['line1'], tle2['line2'], str(tle2['name']))
            cd.get_distance(es1, es2)
            j += 1

with tab1:
    st.header("Overview of Closest Distances")

    rows = db.get_distances()
    if rows:
        df = pd.DataFrame(rows, columns=["sat1_name", "sat2_name", "min_distance", "closest_time"])

        # Rename columns for display
        df.rename(columns={
            "sat1_name": "Satellite1",
            "sat2_name": "Satellite2",
            "min_distance": "Minimum Distance (KM)",
            "closest_time": "Time (UTC)"
        }, inplace=True)

        # Format with color scale (green = safe, red = risky)
        def color_scale(val):
            if val < 80:
                color = "red"
            elif val < 100:
                color = "orange"
            else:
                color = "green"
            return f"background-color: {color}; color: white"

        st.dataframe(df.style.applymap(color_scale, subset=["Minimum Distance (KM)"]))
    else:
        st.warning("No distance data available yet.")


    # Display each row individually with a button
    for i, row in df.iterrows():
        col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 2, 1])
        col1.write(row["Satellite1"])
        col2.write(row["Satellite2"])
        col3.write(row["Minimum Distance (KM)"])
        col4.write(row["Time (UTC)"])
        button_key = f"plot_{i}"
        if col5.button("Show Plot", key=button_key):
            # Get TLEs for satellites
            tle1_data = db.get_tle(row["Satellite1"])
            tle2_data = db.get_tle(row["Satellite2"])

            if tle1_data and tle2_data:
                sat1 = EarthSatellite(tle1_data['line1'], tle1_data['line2'], tle1_data['name'])
                sat2 = EarthSatellite(tle2_data['line1'], tle2_data['line2'], tle2_data['name'], )
                times, distances = cd.get_distance(sat1, sat2)

                # Plot distances over time
                plt.figure(figsize=(10, 5))
                plt.plot(times, distances, marker='o')
                plt.title(f"Distance Over Time: {row['Satellite1']} - {row['Satellite2']}")
                plt.xlabel("Time (UTC)")
                plt.ylabel("Distance (KM)")
                plt.xticks(rotation=45)
                plt.grid(True)
                st.pyplot(plt)
            else:
                st.warning("TLE data not found for one or both satellites.")

db.close()
