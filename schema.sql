CREATE ROLE "www-data" LOGIN;
CREATE ROLE "sousvide" LOGIN;
CREATE ROLE "daniel" LOGIN;
CREATE ROLE "chef";
GRANT "chef" TO "daniel";

CREATE DATABASE "sousvide";
\c sousvide

CREATE TABLE orders (
    order_id serial primary key,
    name text not null,
    start_time timestamp with time zone not null,
    end_time timestamp with time zone not null,
    target_temperature double precision not null,

    CONSTRAINT end_after_start CHECK ( end_time >= start_time ),
    CONSTRAINT interval_size CHECK ( end_time - start_time < interval '3 hours' )
);

CREATE TABLE temperatures (
    sensor_name text not null,
    time timestamp with time zone not null,
    reading double precision not null,

    PRIMARY KEY (sensor_name, time)
);

CREATE TABLE control_log (
    time timestamp with time zone not null primary key,
    in_response_to_order integer REFERENCES orders (order_id),
    failed boolean not null,
    power double precision not null
);

GRANT SELECT ON temperatures TO "www-data";
GRANT SELECT ON control_log  TO "www-data";
GRANT SELECT ON orders       TO "www-data";

GRANT SELECT ON orders       TO "sousvide";
GRANT INSERT ON temperatures TO "sousvide";
GRANT INSERT ON control_log  TO "sousvide";

GRANT INSERT ON orders TO "chef";
GRANT SELECT, UPDATE ON orders_order_id_seq TO "chef";
