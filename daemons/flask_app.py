#!/usr/bin/python3

from flask import Flask, jsonify
from sousvide_shared import printt, sousvidedb

app = Flask(__name__)

@app.route("/status")
def hello():
    with sousvidedb() as db_cur:
        db_cur.execute("SET TimeZone='Europe/London'")
        db_cur.execute("""
            SELECT control_log.power         AS control_log_power,
                   control_log.failed        AS control_log_failed,
                   orders.name               AS order_name,
                   orders.start_time         AS order_start_time,
                   orders.end_time           AS order_end_time,
                   orders.target_temperature AS order_target_temperature
            FROM control_log
            LEFT JOIN orders ON orders.order_id = control_log.in_response_to_order
            WHERE control_log.time > current_timestamp - interval '1 minute'
            ORDER BY control_log.time DESC
            LIMIT 1
        """)

        data = db_cur.fetchone()

        db_cur.execute("""
            SELECT reading
            FROM temperatures
            WHERE time > current_timestamp - interval '1 minute'
            ORDER BY time DESC
            LIMIT 1
        """)

        data2 = db_cur.fetchone()

    if data is None:
        return jsonify({"error": "state unknown"}), 400

    data = dict(data)

    if data2 is None:
        data["current_temperature"] = None
    else:
        data["current_temperature"] = data2["reading"]

    # The default way these get stringed is weird. Apparently calling str()
    # forces them into a nicer format.
    for key in ("order_start_time", "order_end_time"):
        data[key] = str(data[key])

    return jsonify(data)

def decimate(data):
    last_minute = None

    for idx, value in enumerate(data):
        this_minute = value["time"].replace(second=0, microsecond=0)

        # last 60 points at high resolution
        if idx > data.rowcount - 60:
            yield value
        elif last_minute != this_minute:
            last_minute = this_minute
            yield value

@app.route("/time-series")
def temperatures():
    temperatures = []
    powers = []

    with sousvidedb() as db_cur:
        db_cur.execute("SET TimeZone='Europe/London'")

        db_cur.execute("""
            SELECT time, reading
            FROM temperatures
            WHERE time > current_timestamp - interval '5 hours'
            ORDER BY time
        """)

        for row in decimate(db_cur):
            temperatures.append((str(row["time"]), row["reading"]))

        db_cur.execute("""
            SELECT time, power
            FROM control_log
            WHERE time > current_timestamp - interval '5 hours'
        """)

        for row in decimate(db_cur):
            powers.append((str(row["time"]), row["power"]))

    return jsonify(temperatures=temperatures, powers=powers)
