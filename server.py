from flask import Flask
from flask import request
from pathlib import Path
import sqlite3


app = Flask(__name__)

@app.route("/health", methods=["GET"])
def health():
    status = "{\"status\" : \"ok\"}"
    return status

BACKEND_DB = Path(__file__).resolve().parent / "database" / "backend_database.db"

@app.route("/readings", methods=["POST"])
def receive_reading():
    data = request.get_json()

    con = sqlite3.connect(BACKEND_DB)
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS readings(id, device_id, timestamp, water_level_m)")
    cur.execute("INSERT INTO readings VALUES(?, ?, ?, ?)",
        (
        data["id"], 
        data["device_id"],
        data["timestamp"], 
        data["water_level_m"]
        )
    )
    con.commit()
    level = data.get("water_level_m")
    con.close()
    if isinstance(level, bool) or not isinstance(level,(float, int)):
        return{"error": "required measurement is missing or it is not a number"}, 400
    else: 
        return {"received": level}, 200
    

@app.route("/readings", methods=["GET"])
def get_reading():
    con = sqlite3.connect(BACKEND_DB)
    con.row_factory = sqlite3.Row #let every row in db can be called by row.
    try:
        cur = con.cursor()
        cur.execute("""
        SELECT id, device_id, timestamp, water_level_m 
        FROM readings 
        ORDER BY timestamp DESC
        LIMIT 10
        """)
        readings = [dict(row) for row in cur.fetchall()]
        return {"readings": readings}, 200
    finally:
        con.close()
        