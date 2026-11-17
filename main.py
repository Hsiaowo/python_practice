import sensors.device as device
from datetime import datetime
import sqlite3
import time
from pathlib import Path
import requests
"""
example_jsn = {"water_level_reading": 1.25}
response = requests.post(
    "http://127.0.0.1:5000/readings",
    json=example_jsn,
    timeout=5,
)
print(response.status_code)
print(response.json())

"""

db_path = Path(__file__).resolve().parent / "database" /"offline_database.db"
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS readings(id, device_id, timestamp, water_level_m)")
con.commit()

for row in cur.execute("""
        SELECT id, device_id, timestamp, water_level_m 
        FROM readings ORDER BY timestamp DESC \
        LIMIT 10"""):
    print(row)

while True:
    id = 1
    device_id = 123382
    timestamp = datetime.now().astimezone().isoformat()
    water_level_m = device.read_sensor()
    data = (id, device_id, timestamp, water_level_m)


    data_json = {
        "id": id, 
        "device_id": device_id,
        "timestamp": timestamp, 
        "water_level_m": water_level_m 
    }

    'data storage in offline database'
    print(f"{datetime.now()}")
    print(f"{device.read_sensor()}\n")
    cur.execute("INSERT INTO readings VALUES(?, ?, ?, ?)", data)
    con.commit()

    'data storage in backend database'
    response = requests.post(
        "http://127.0.0.1:5000/readings",
        json=data_json, 
        timeout=5
    )




    time.sleep(2)

