#!/usr/bin/python3

import os, os.path
import time
import psycopg2

def read_temperature():
    base = "/sys/bus/w1/devices"
    for name in os.listdir(base):
        try:
            with open(os.path.join(base, name, "w1_slave")) as f:
                status = f.readline()
                if not status.endswith("YES"):
                    raise Exception("bad status", status)
                data = f.readline()
                _, t_equals, value = data.partition("t=")
                if not t_equals = "t=":
                    raise Exception("expected t=", data)
                value = int(value) / 1000.
                if f.readline() != "":
                    raise Exception("expected two lines")
                yield (name, value)
        except:
            pass

def cycle():
    db_conn = psycopg2.connect(dbname="sousvide")
    db_conn.autocommit = True
    db_cur = db_conn.cursor ()

    for temp_name, temp_value in read_temperature():
        print("Read temperature:", temp_name, temp_value)
        db_cur.execute("INSERT INTO temperatures (sensor_name, time, reading) \
                        VALUES (%s, current_time, %s)",
                        (temp_name, temp_value))

def main():
    while True:
        cycle()
        time.sleep(1)
