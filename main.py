import sensors.device as device
from datetime import datetime
import sqlite3
import time
from pathlib import Path


db_path = Path(__file__).resolve().parent /"database.db"
con = sqlite3.connect(db_path)
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS data(readings, time)")
con.commit()

for row in cur.execute("SELECT time, readings from data ORDER BY time DESC"):
    print(row)
"""
while True:
    times = datetime.now()
    device_reading = device.read_sensor()
    data = (times, device_reading)
    print(f"{datetime.now()}")
    print(f"{device.read_sensor()}\n")
    cur.execute("INSERT INTO data VALUES(?, ?)", data)
    con.commit()
    time.sleep(2)
 """