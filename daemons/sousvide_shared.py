#!/usr/bin/python3

import sys
import datetime
import psycopg2, psycopg2.extras
from contextlib import contextmanager

@contextmanager
def sousvidedb():
    with psycopg2.connect(dbname="sousvide") as db_conn:
        db_conn.autocommit = True
        with db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as db_cur:
            yield db_cur

def printt(*args, **kwargs):
    print(datetime.datetime.now(), *args, **kwargs, file=sys.stderr)
