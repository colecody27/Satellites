import numpy as np
from skyfield.api import load, EarthSatellite
from datetime import datetime, timezone


class CollisionDetector:
    def __init__(self, times_per_hour, db):
        self.ts = load.timescale()
        self.today = datetime.now(timezone.utc).date()
        self.times_per_hour = times_per_hour
        self.db = db

    def get_distance(self, sat1, sat2):
        ts = load.timescale()
        year, month, day = self.today.year, self.today.month, self.today.day
        minutes = range(0, 24 * self.times_per_hour)  # 24 hours * 6 steps per hour = 10-min steps
        times = ts.utc(year, month, day, 0, minutes)

        # shape: [[x, x, x], [y, y, y],...] for each time
        pos1 = sat1.at(times).position.km  
        pos2 = sat2.at(times).position.km

        # Vectorized distance calculation
        distances = np.linalg.norm(pos1 - pos2, axis=0)  # axis=0 because positions are columns

        min_distance = round(np.min(distances), 3)
        min_index = np.argmin(distances)
        closest_time = times[min_index].utc_datetime()

        print(f"Minimum distance from {sat1.name} and {sat2.name} is {min_distance} km at time {closest_time}")
        self.db.log_distance(sat1.name, sat2.name, min_distance, closest_time)
