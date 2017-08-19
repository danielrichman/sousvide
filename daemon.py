#!/usr/bin/python3

import os, os.path
import time
import psycopg2

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
            print("Failed to read temperature", exn)

        else:
            yield (name, value)

def cycle():
    db_conn = psycopg2.connect(dbname="sousvide")
    db_conn.autocommit = True
    db_cur = db_conn.cursor ()

    for temp_name, temp_value in read_temperature():
        print("Read temperature:", temp_name, temp_value)
        db_cur.execute("INSERT INTO temperatures (sensor_name, time, reading) \
                        VALUES (%s, current_timestamp, %s)",
                        (temp_name, temp_value))

    db_cur.close()
    db_conn.close()

def main():
    while True:
        cycle()
        time.sleep(1)

if __name__ == "__main__":
    main()
