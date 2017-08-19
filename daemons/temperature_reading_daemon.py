#!/usr/bin/python3

import os, os.path
import time

from sousvide_shared import printt, sousvidedb

def read_temperatures():
    base = "/sys/bus/w1/devices"

    printt("Starting to read temperatures.")

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

                if value == 0:
                    raise Exception("temperature is not allowed to be precisely zero "
                                    "because a disconnected sensor sometimes shows up as zero")

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

def cycle():
    start_time = time.time()
    temperatures = list(read_temperatures())

    with sousvidedb() as db_cur:
        log_temperatures(temperatures, db_cur)

    sleep_for = start_time + 1 - time.time()
    printt("Sleeping for", sleep_for)
    time.sleep(max(sleep_for, 0))

def main():
    while True:
        cycle()

if __name__ == "__main__":
    main()
