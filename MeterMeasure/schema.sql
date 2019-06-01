-- Initialize the database.
-- Drop any existing data and create empty tables.

DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS records;
DROP TABLE IF EXISTS recordValueStore;
DROP TABLE IF EXISTS recordTagGroups;

CREATE TABLE users (
    ID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    UNIQUE(username)--, -- this will ensure that each user is unique.
--    UNIQUE(username, password) -- this will ensure that users cannot
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


INSERT INTO recordValueStore VALUES (5, null, null, 0.9);
INSERT INTO recordValueStore VALUES (6, null, null, 0.8);
INSERT INTO recordValueStore VALUES (7, null, null, 0.5);


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


INSERT INTO users(ID, username, password) VALUES (0, 'JohnDoe', 'pass');
INSERT INTO users(ID, username, password) VALUES (1, 'MatthewRaison', 'ThisIsMyPassword');