#!/usr/bin/python3

import os, os.path
import time, datetime
import psycopg2

def printt(*args, **kwargs):
    print(datetime.datetime.now(), *args, **kwargs)

def read_temperature():
    base = "/sys/bus/w1/devices"

    for name in os.listdir(base):
        if name == "w1_bus_master1":
            continue

        try:
            with open(os.path.join(base, name, "w1_slave")) as f:
                status = f.readline().strip()
                data = f.readline().strip()
                if f.readline() != "":
                    raise Exception("expected two lines")

                if not status.endswith("YES"):
                    raise Exception("bad status", status)
                _, t_equals, value = data.partition("t=")
                if t_equals != "t=":
                    raise Exception("expected t=", data)

                value = int(value) / 1000.

        except Exception as exn:
            printt("Failed to read temperature", exn)

        else:
            printt("Read temperature:", name, value)
            yield (name, value)

def log_temperatures(temperatures, db_cur):
    for temp_name, temp_value in temperatures:
        db_cur.execute("INSERT INTO temperatures (sensor_name, time, reading) \
                        VALUES (%s, current_timestamp, %s)",
                        (temp_name, temp_value))

def get_order(db_cur):
    db_cur.execute("""
        SELECT * FROM orders
        WHERE start_time < current_timestamp AND current_timestamp < end_time
        ORDER BY seqno DESC 
        LIMIT 1
    """)

    return db_cur.fetchone()

class Decision:
    def __init__(self, in_response_to_order, failed, power):
        self.in_response_to_order = in_response_to_order
        self.failed = failed
        self.power = power

def artificial_intelligence(order, temperatures):
    if order is None:
        printt("Have no orders: switching off")
        return Decision(in_response_to_order=None, failed=False, power=0.)

    printt("Current order:", order["name"], "target", order["target_temperature"])
    in_response_to_order = order["order_id"]

    if not temperatures:
        printt("No temperature readings: switching off")
        return Decision(in_response_to_order=in_response_to_order, failed=True, power=0.)
    
    (sensor_name, sensor_value), _ = temperatures
    printt("Using temperature sensor", temp_name, "value", temp_value)

    if sensor_value < order["target_temperature"]:
        power = 0.8
    else:
        power = 0.2

    return Decision(in_response_to_order=in_response_to_order, failed=False, power=power)

def decide_what_to_do_and_return_power():
    db_conn = psycopg2.connect(dbname="sousvide")
    db_conn.autocommit = True
    db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

    temperatures = list(read_temperature())
    log_temperatures(temperatures, db_cur)

    decision = artificial_intelligence(order, temperatures)

    db_cur.execute("INSERT INTO control_log (time, in_response_to_order, failed, power) \
                    VALUES (current_time, %s, %s, %s)"
                   (decision.in_response_to_order, decision.failed, decision.power))

    db_cur.close()
    db_conn.close()

    return decision.power

def apply_fire(power):
    on_for = power * 10.
    off_for = (1. - power) * 10.

    assert on_for >= 0. && off_for >= 0. ** abs(on_for + off_for - 10.) < 0.001

    printt("Powering on for", on_for)
    with open("/etc/sousvide-pin") as f:
        f.write("1")

    time.sleep(on_for)

    printt("Leaving off for", off_for)
    with open("/etc/sousvide-pin") as f:
        f.write("0")

    time.sleep(off_for)

def main():
    while True:
        power = decide_what_to_do_and_return_power()
        apply_fire(power)

if __name__ == "__main__":
    main()
