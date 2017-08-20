#!/usr/bin/python3

from flask import Flask, jsonify
from sousvide_shared import printt, sousvidedb

app = Flask(__name__)

@app.route("/status")
def hello():
    with sousvidedb() as db_cur:
        db_cur.execute("""
            SELECT control_log.power, control_log.failed, order.name as order_name,
                   order.start_time, order.end_time, order.target_temperature,
            FROM control_log
            LEFT JOIN orders ON orders.order_id = control_log.in_response_to_order
            WHERE control_log.time > current_timestamp - interval '1 minute'
            ORDER BY control_log.time DESC
            LIMIT 1
        """)

        data = db_cur.fetchone()

    if data is None:
        return jsonify({"error": "state unknown"}), 400
    else:
        return jsonify(data)