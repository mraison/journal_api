-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS doctors;
DROP TABLE IF EXISTS locations;
DROP TABLE IF EXISTS doctor_locations;
DROP TABLE IF EXISTS doctor_schedule;
DROP TABLE IF EXISTS appointment_time_chunks;

CREATE TABLE doctors (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL
);

CREATE TABLE locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  address TEXT NOT NULL
);

CREATE TABLE doctor_locations (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  FOREIGN KEY (doctor_id) REFERENCES doctors (id),
  FOREIGN KEY (location_id) REFERENCES locations (id)
);

CREATE TABLE doctor_schedule (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  doctor_id INTEGER NOT NULL,
  -- We'll assume that the day is represented by digets 0-6 where 0 is Sunday and 6 is Saturday
  day_enumerated INTEGER NOT NULL,
  -- Assume these are chunked into 30 minutes increments where 0 is the time 00:00 to 00:30.
  -- This means the range of this field is between 0 and 47, since 47 would be 23:30 to 24:00
  thirty_minute_time_segment INTEGER NOT NULL,
  UNIQUE(doctor_id, day_enumerated, thirty_minute_time_segment)
);

CREATE TABLE appointment_time_chunks (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  -- Since appointments can vary in length we'll need some way to group them together.
  -- The constants for any given appointment are the doctor and the location so we'll use a
  -- hash of the doctor_id, location_id, and timeslots used to group together these appoitnment time slots.
  appointment_hash_id TEXT NOT NULL,
  doctor_schedule_id INTEGER NOT NULL,
  location_id INTEGER NOT NULL,
  FOREIGN KEY (doctor_schedule_id) REFERENCES doctor_schedule (id),
  FOREIGN KEY (location_id) REFERENCES locations (id),
  UNIQUE(doctor_schedule_id)
);


INSERT INTO doctors(id, first_name, last_name) VALUES (0, 'John', 'Doe');
INSERT INTO doctors(id, first_name, last_name) VALUES (1, 'Jane', 'Smith');

INSERT INTO locations(id, address) VALUES (0, '123 Main St');
INSERT INTO locations(id, address) VALUES (1, '456 Central St');

INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (0, 0, 0);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (1, 1, 0);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (2, 1, 1);

-- For testing we're going to imagine that doctor John Doe only works on Monday from 9am till noon.
-- 9am-9:30am is 19 and 11:30am-12:00pm is 23
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (0, 0, 1, 19);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (1, 0, 1, 20);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (2, 0, 1, 21);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (3, 0, 1, 22);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (4, 0, 1, 23);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (5, 0, 1, 24);

-- Lets set a default appointment for doctor John Doe at 123 Main St from 9am-10am.
INSERT INTO appointment_time_chunks(id, appointment_hash_id, doctor_schedule_id, location_id) VALUES (0, '00_119_120', 0, 0);
INSERT INTO appointment_time_chunks(id, appointment_hash_id, doctor_schedule_id, location_id) VALUES (1, '00_119_120', 1, 0);