import requests
import json
from skyfield.api import load, EarthSatellite
import numpy as np
from db import TLEDatabase 
from Collision_Detector import CollisionDetector
from datetime import datetime, timedelta, timezone

"""
Collision tracker
    - Call API Get TLE of 2 elements (http://tle.ivanstanojevic.me/api/tle)
    - 
"""
HEADERS = {
    "User-Agent": "xxxx",
    "Accept": "application/json"
    }

db = TLEDatabase()
cd = CollisionDetector(6, db)
tles = None

# Get satellites TLEs
try:
    last_update = db.get_last_updated()
    print(last_update)

    # Compare with current UTC time
    threshold = timedelta(hours=1)
    now = datetime.now(timezone.utc)
    if not last_update or now - last_update >= threshold:
        response = requests.get("http://tle.ivanstanojevic.me/api/tle", headers=HEADERS)
        response.raise_for_status()  # Raise an exception for HTTP errors
        tles = response.json()['member']
except requests.exceptions.RequestException as e:
    print(f"Error fetching TLE data: {e}")

print(f"TLEs: {tles}")
if tles:
    for tle in tles:
        db.insert_or_update_tle(
            tle['satelliteId'],
            tle['name'],
            tle['line1'],
            tle['line2'],
            tle['date']
        )

print(db.fetch_all())

sat1 = db.fetch_tle(35932)
sat2 = db.fetch_tle(25544)

es1 = EarthSatellite(sat1['line1'], sat1['line2'], sat1['sat_id'])
es2 = EarthSatellite(sat2['line1'], sat2['line2'], sat2['sat_id'])
cd.get_distance(es1, es2)

db.close()
