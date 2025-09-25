import sqlite3
from datetime import datetime, timezone

class TLEDatabase:
    def __init__(self, db_file="satellites.db"):
        self.conn = sqlite3.connect(db_file)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS tle (
            sat_id TEXT PRIMARY KEY,
            name TEXT,
            line1 TEXT,
            line2 TEXT,
            date TEXT,
            fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS distances (
            sat1_id TEXT,
            sat2_id TEXT,
            min_distance REAL,
            closest_time TEXT,
            run_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        self.conn.commit()

    def insert_or_update_tle(self, sat_id, name, line1, line2, date):
        self.cursor.execute("""
        INSERT INTO tle (sat_id, name, line1, line2, date, fetched_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(sat_id) DO UPDATE SET
            name=excluded.name,
            line1=excluded.line1,
            line2=excluded.line2,
            date=excluded.date,
            fetched_at=CURRENT_TIMESTAMP
        """, (sat_id, name, line1, line2, date, datetime.now(timezone.utc)))
        self.conn.commit()

    def fetch_tle(self, sat_id):
        self.cursor.execute("SELECT * FROM tle WHERE sat_id=?", (sat_id,))
        item = self.cursor.fetchone()
        print(f"Type: {type(item)}")
        return {
            'sat_id': str(item[0]),
            'line1': item[2],
            'line2': item[3],
        }

    def fetch_all(self):
        self.cursor.execute("SELECT * FROM tle")
        return self.cursor.fetchall()

    def log_distance(self, sat1_id, sat2_id, min_distance, closest_time):
        self.cursor.execute("""
        INSERT INTO distances (sat1_id, sat2_id, min_distance, closest_time)
        VALUES (?, ?, ?, ?)
        """, (sat1_id, sat2_id, min_distance, closest_time))
        self.conn.commit()
    
    def get_last_updated(self):
        self.cursor.execute("""SELECT MAX(fetched_at) FROM tle""")
        time = self.cursor.fetchone()[0]
        return datetime.fromisoformat(time) if time else None

    def close(self):
        self.conn.close()
