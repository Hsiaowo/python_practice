import sensors.device as device
from datetime import datetime
import sqlite3
import time
from pathlib import Path

 
db_path = Path(__file__).resolve().parent / "database" /"database.db"
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS readings(id, device_id, timestamp, water_level_m)")
con.commit()

for row in cur.execute("SELECT id, device_id, timestamp, water_level_m from readings ORDER BY timestamp DESC"):
    print(row)

"""while True:
    id = 1
    device_id = 123382
    timestamp = datetime.now()
    water_level_m = device.read_sensor()
    data = (id, device_id, timestamp, water_level_m)
    print(f"{datetime.now()}")
    print(f"{device.read_sensor()}\n")
    cur.execute("INSERT INTO readings VALUES(?, ?, ?, ?)", data)
    con.commit()
    time.sleep(2)
"""