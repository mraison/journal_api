-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS recordValueStore;
DROP TABLE IF EXISTS recordTagGroups;

CREATE TABLE users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL
);

CREATE TABLE records (
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  unixTime INT NOT NULL, -- Unix time stamp interpretation of the time.
-- removing this for now because I like the timestamp better.
--  dateTimeString TEXT NOT NULL, -- ISO8601 format datetime string: YYYY-MM-DD, HH:MM:SS.MMM
  metricUnits TEXT NOT NULL, -- The is the units we're measuring in. This could be anything like lbs to percentages.
  -- I want flexibility in how I'm recording so I'm going to have this point to a separate "values" table.
  -- This table will include columns for the different data types: INT, TEXT, and REAL
  metricValueIDPointer INT NOT NULL,
  notes TEXT,
  FOREIGN KEY (metricValueIDPointer) REFERENCES recordValueStore (ID)
--  FOREIGN KEY (userID) REFERENCES users (ID)
);

CREATE TABLE recordValueStore (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    intVal INT,
    strVal TEXT,
    floatVal REAL
);

CREATE TABLE recordTagGroups (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    tagGroupName TEXT,
    userID INT NOT NULL,
    recordIDPointer INT NOT NULL,
    FOREIGN KEY (recordIDPointer) REFERENCES records (ID)
--    UNIQUE(userID, tagGroupName) -- Can't have two groups named the same thing.
);

INSERT INTO users(ID, firstName, lastName) VALUES (0, 'John', 'Doe');
INSERT INTO users(ID, firstName, lastName) VALUES (1, 'Matthew', 'Raison');


INSERT INTO recordValueStore VALUES (0, 1, null, null);
INSERT INTO recordValueStore VALUES (1, 1, null, null);
INSERT INTO recordValueStore VALUES (2, 1, null, null);
INSERT INTO recordValueStore VALUES (3, 2, null, null);
INSERT INTO recordValueStore VALUES (4, 3, null, null);


INSERT INTO recordValueStore VALUES (5, null, '90%', null);
INSERT INTO recordValueStore VALUES (6, null, '80%', null);
INSERT INTO recordValueStore VALUES (7, null, '50%', null);


INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (0, 1557453366, 'meters', 0, 'Test metric record in meters.');
INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (1, 1557453426, 'meters', 1, 'Test metric record in meters.');
INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (2, 1557453458, 'meters', 2, 'Test metric record in meters.');
INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (3, 1557453366, 'feet', 3, 'Test metric record in feet.');
INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (4, 1557453426, 'feet', 4, 'Test metric record in feet.');


INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (5, 1557453366, 'percentage', 5, 'Test metric record in percentage.');
INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (6, 1557453426, 'percentage', 6, 'Test metric record in percentage.');
INSERT INTO records(ID, unixTime, metricUnits, metricValueIDPointer, notes)
    VALUES (7, 1557453458, 'percentage', 7, 'Test metric record in percentage.');


INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (0, 'How far can I throw a base ball', 0, 0);
INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (1, 'How far can I throw a base ball', 0, 1);
INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (2, 'How far can I throw a base ball', 0, 2);

INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (3, 'Sunflow Growth', 0, 3);
INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (4, 'Sunflow Growth', 0, 4);


INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (5, 'Heart Rate Cap.', 1, 5);
INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (6, 'Heart Rate Cap.', 1, 6);
INSERT INTO recordTagGroups(ID, tagGroupName, userID, recordIDPointer)
    VALUES (7, 'Heart Rate Cap.', 1, 7);

--
--INSERT INTO doctors(id, first_name, last_name) VALUES (0, 'John', 'Doe');
--INSERT INTO doctors(id, first_name, last_name) VALUES (1, 'Jane', 'Smith');
--
--INSERT INTO locations(id, address) VALUES (0, '123 Main St');
--INSERT INTO locations(id, address) VALUES (1, '456 Central St');
--
--INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (0, 0, 0);
--INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (1, 1, 0);
--INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (2, 1, 1);
--
---- For testing we're going to imagine that doctor John Doe only works on Monday from 9am till noon.
---- 9am-9:30am is 19 and 11:30am-12:00pm is 23
--INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (0, 0, 1, 19);
--INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (1, 0, 1, 20);
--INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (2, 0, 1, 21);
--INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (3, 0, 1, 22);
--INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (4, 0, 1, 23);
--INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (5, 0, 1, 24);
--
---- Lets set a default appointment for doctor John Doe at 123 Main St from 9am-10am.
--INSERT INTO appointment_time_chunks(id, appointment_hash_id, doctor_schedule_id, location_id) VALUES (0, '00_119_120', 0, 0);
--INSERT INTO appointment_time_chunks(id, appointment_hash_id, doctor_schedule_id, location_id) VALUES (1, '00_119_120', 1, 0);