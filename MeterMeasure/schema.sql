-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS measurements;
DROP TABLE IF EXISTS joinMeasurementsToRecordSet;
DROP TABLE IF EXISTS recordSet;
DROP TABLE IF EXISTS recordSetPermissionGroups;

CREATE TABLE users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE(username)
);

-- measurements
CREATE TABLE measurements (
  ID INTEGER PRIMARY KEY AUTOINCREMENT,
  unixTime INT NOT NULL, -- Unix time stamp interpretation of the time.
-- removing this for now because I like the timestamp better.
--  dateTimeString TEXT NOT NULL, -- ISO8601 format datetime string: YYYY-MM-DD, HH:MM:SS.MMM
  units TEXT NOT NULL, -- The is the units we're measuring in. This could be anything like lbs to percentages.
  -- I want flexibility in how I'm recording so I'm going to have this point to a separate "values" table.
  -- This table will include columns for the different data types: INT, TEXT, and REAL
  intVal INT,
  strVal TEXT,
  floatVal REAL,
  notes TEXT,
  UNIQUE(ID)
);

-- data point series definition
CREATE TABLE joinMeasurementsToRecordSet (
    recordSetID INT NOT NULL, -- At the minimum we want the "None" group...
    measurementsID INT NOT NULL,
    FOREIGN KEY (measurementsID) REFERENCES measurements (ID),
    FOREIGN KEY (recordSetID) REFERENCES recordSet (ID),
    UNIQUE(recordSetID, measurementsID)
    -- any point can only be included in a group once. (no repetition of measurement instances.)
--    UNIQUE(userID, tagGroupName)
--    UNIQUE(recordIDPointer) -- I'm going to leave this requirement out for the time being.
-- In most cases you'll want only one record set to be associated with a group of measurements unless for example when
-- the subject you are measuring is part of a larger set of things to be measured. I.E. if you measure your height and want to track
-- both your height over time and people height over time generally.
);

-- sets of points for a users records.
CREATE TABLE recordSet (
    -- name bits
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    --           + owner bit
    userID INT NOT NULL, -- This is the owner

    -- group bits
    recSetPermGroupName TEXT,

    -- permission bits
    ownerPermissions TEXT NOT NULL, -- either '', 'r', 'w', or 'rw'
    groupPermissions TEXT NOT NULL, -- either '', 'r', 'w', or 'rw'
    allPermissions   TEXT NOT NULL, -- either '', 'r', 'w', or 'rw'
    -- owerID INT NOT NULL this is going to be the same as the userID
    UNIQUE(ID),
    UNIQUE(name, userID),
    FOREIGN KEY (recSetPermGroupName) REFERENCES recordSetPermissionGroups (name),
    FOREIGN KEY (userID) REFERENCES users (ID)
);

-- all the user groups and people in them.
CREATE TABLE recordSetPermissionGroups (
    name TEXT NOT NULL,
    userID INT,
    UNIQUE(name, userID),
    FOREIGN KEY (userID) REFERENCES users (ID)
);


-- Set up initial users...
INSERT INTO users(ID, username, password) VALUES (0, 'JohnDoe', 'pass');
INSERT INTO users(ID, username, password) VALUES (1, 'MatthewRaison', 'ThisIsMyPassword');

-- Set up initial user groups...
INSERT INTO recordSetPermissionGroups (name, userID) VALUES ('DEVELOPER', 0);
INSERT INTO recordSetPermissionGroups (name, userID) VALUES ('DEVELOPER', 1);


-- First thing first we need to create a record set to put our measurements:
INSERT INTO recordSet (
    ID,
    name,
    userID,
    recSetPermGroupName,
    ownerPermissions,
    groupPermissions,
    allPermissions
) VALUES (0, 'test set A', 1, 'DEVELOPER', 'rw', 'r', '');
-- Now we can record stuff and add them to this set.
-- Create the values...

-- Add in measurement metadata that makes this an actual measurement.
INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (0, 1557453366, 'meters', 1, null, null, 'Test metric record in meters.');
-- Now join it to the record set
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (0, 0);

-- Repeat
INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (1, 1557453426, 'meters', 1, null, null, 'Test metric record in meters.');
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (0, 1);

-- Repeat
INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (2, 1557453456, 'meters', 1, null, null, 'Test metric record in meters.');
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (0, 2);




-- First thing first we need to create a record set to put our measurements:
INSERT INTO recordSet (
    ID,
    name,
    userID,
    recSetPermGroupName,
    ownerPermissions,
    groupPermissions,
    allPermissions
) VALUES (1, 'test set B', 1, 'DEVELOPER', 'rw', 'r', '');
INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (3, 1557453366, 'percentage', null, null, 0.20, 'Heart rate cap.');
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (1, 3);

-- Repeat
INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (4, 1557453426, 'percentage', null, null, 0.22, 'Heart rate cap.');
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (1, 4);

-- Repeat
INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (5, 1557453456, 'percentage', null, null, 0.30, 'Heart rate cap.');
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (1, 5);

INSERT INTO measurements (ID, unixTime, units, intVal, strVal, floatVal, notes) VALUES (6, 1557453456, 'percentage', null, null, 0.52, 'Heart rate cap.');
INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) VALUES (1, 6);
