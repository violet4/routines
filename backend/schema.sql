DROP TABLE activity CASCADE;
DROP TABLE occurrence;
DROP TYPE day;

BEGIN;

CREATE TYPE day AS ENUM (
    'sunday'
    , 'monday'
    , 'tuesday'
    , 'wednesday'
    , 'thursday'
    , 'friday'
    , 'saturday'
);

CREATE TABLE activity (
    activity_id SERIAL PRIMARY KEY
    , title TEXT NOT NULL
);

CREATE TABLE occurrence (
    occurence_id SERIAL PRIMARY KEY
    , activity_id INTEGER NOT NULL REFERENCES activity(activity_id)
    , day day NOT NULL
    , time TIME NOT NULL
);

INSERT INTO activity (title) VALUES ('brush teeth');
INSERT INTO occurrence (day, time, activity_id) VALUES ('sunday', '5:00pm', (SELECT activity_id FROM activity LIMIT 1));

COMMIT;
