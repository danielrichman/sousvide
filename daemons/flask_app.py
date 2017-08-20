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

    if data2 is None:
        data["current_temperature"] = None
    else:
        data["current_temperature"] = data2["reading"]

    # The default way these get stringed is weird. Apparently calling str()
    # forces them into a nicer format.
    for key in ("start_time", "end_time"):
        data[key] = str(data[key])

    return jsonify(dict(data))
