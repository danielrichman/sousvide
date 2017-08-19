#!/usr/bin/python3

import time
from sousvide_shared import printt, sousvidedb

def get_temperature(db_cur):
    db_cur.execute("""
        SELECT *, (current_timestamp - time) as recency
        FROM temperatures
        ORDER BY time DESC
        LIMIT 1
    """)

    return db_cur.fetchone()

def get_order(db_cur):
    db_cur.execute("""
        SELECT * FROM orders
        WHERE start_time < current_timestamp AND current_timestamp < end_time
        ORDER BY order_id DESC 
        LIMIT 1
    """)

    return db_cur.fetchone()

class Decision:
    def __init__(self, in_response_to_order, failed, power):
        self.in_response_to_order = in_response_to_order
        self.failed = failed
        self.power = power

def artificial_intelligence(order, temperature):
    if order is None:
        printt("Have no orders: switching off")
        return Decision(in_response_to_order=None, failed=False, power=0.)

    target_temperature = order["target_temperature"]
    in_response_to_order = order["order_id"]

    printt("Current order:", order["name"], "target", target_temperature)

    if not temperature:
        printt("No temperature readings: switching off")
        return Decision(in_response_to_order=in_response_to_order, failed=True, power=0.)

    temperature_reading = temperature["reading"]
    temperature_recency = temperature["recency"]

    printt("Temperature reading", 
           temperature["sensor_name"], temperature_reading,
           "at", temperature["time"], "recency:", temperature_recency)

    if temperature_recency.total_seconds() > 10:
        printt("Temperature insufficiently recent: switching off")
        return Decision(in_response_to_order=in_response_to_order, failed=True, power=0.)
 
    if temperature_reading < target_temperature:
        power = 0.8
    else:
        power = 0.2

    return Decision(in_response_to_order=in_response_to_order, failed=False, power=power)

def decide_what_to_do_and_return_power():
    with sousvidedb() as db_cur:
        temperature = get_temperature(db_cur)
        order = get_order(db_cur)

        decision = artificial_intelligence(order, temperature)

        db_cur.execute("INSERT INTO control_log (time, in_response_to_order, failed, power) \
                        VALUES (current_timestamp, %s, %s, %s)",
                       (decision.in_response_to_order, decision.failed, decision.power))

    return decision.power

def apply_fire(power):
    on_for = power * 10.
    off_for = (1. - power) * 10.

    assert on_for >= 0. and off_for >= 0. and abs(on_for + off_for - 10.) < 0.001

    printt("Powering on for", on_for)
    with open("/etc/sousvide-pin", "w") as f:
        f.write("1")

    time.sleep(on_for)

    printt("Leaving off for", off_for)
    with open("/etc/sousvide-pin", "w") as f:
        f.write("0")

    time.sleep(off_for)

def main():
    while True:
        power = decide_what_to_do_and_return_power()
        apply_fire(power)

if __name__ == "__main__":
    main()
