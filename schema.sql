CREATE ROLE "www-data" LOGIN;
CREATE ROLE "sousvide" LOGIN;
CREATE ROLE "daniel" LOGIN;

CREATE DATABASE "sousvide";
\c sousvide

CREATE TABLE cooking (
    seqno serial primary key,
    name text not null,
    start_time timestamp with time zone not null,
    end_time timestamp with time zone not null,

    last_updated timestamp with time zone,
    current_duty_cycle double precision,
    
    CONSTRAINT end_after_start CHECK ( end_time >= start_time ),
    CONSTRAINT interval_size CHECK ( end_time - start_time < interval '3 hours' )
);

CREATE TABLE temperatures (
    sensor_name text not null,
    time timestamp with time zone not null,
    reading double precision not null,

    PRIMARY KEY (sensor_name, time)
);

GRANT SELECT ON temperatures TO "www-data";
GRANT SELECT ON temperatures TO "daniel";
GRANT SELECT ON cooking TO "www-data";
GRANT SELECT ON cooking TO "sousvide";
GRANT SELECT ON cooking TO "daniel";

GRANT INSERT ON temperatures TO "sousvide";
GRANT UPDATE ( last_updated, current_duty_cycle ) ON cooking TO "sousvide";

GRANT INSERT ON cooking TO "daniel";
GRANT SELECT, UPDATE ON cooking_seqno_seq TO "daniel";
