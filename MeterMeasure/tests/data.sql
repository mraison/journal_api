-- Everything here will get rolled back at the end of a test run
-- Populate everything with known data

DELETE FROM users;
INSERT INTO users(ID, firstName, lastName) VALUES (0, 'John', 'Doe');
INSERT INTO users(ID, firstName, lastName) VALUES (1, 'Matthew', 'Raison');


DELETE FROM recordValueStore;
INSERT INTO recordValueStore VALUES (0, 1, null, null);
INSERT INTO recordValueStore VALUES (1, 1, null, null);
INSERT INTO recordValueStore VALUES (2, 1, null, null);
INSERT INTO recordValueStore VALUES (3, 2, null, null);
INSERT INTO recordValueStore VALUES (4, 3, null, null);

INSERT INTO recordValueStore VALUES (5, null, '90%', null);
INSERT INTO recordValueStore VALUES (6, null, '80%', null);
INSERT INTO recordValueStore VALUES (7, null, '50%', null);


DELETE FROM records;
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (0, 1557453366, datetime('2019-05-09T22:00:00.000'), 'meters', 0, 'Test metric record in meters.');
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (1, 1557453426, datetime('2019-05-09T22:02:00.000'), 'meters', 1, 'Test metric record in meters.');
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (2, 1557453458, datetime('2019-05-09T22:02:32.000'), 'meters', 2, 'Test metric record in meters.');
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (3, 1557453366, datetime('2019-05-09T22:00:00.000'), 'feet', 3, 'Test metric record in feet.');
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (4, 1557453426, datetime('2019-05-09T22:00:01.000'), 'feet', 4, 'Test metric record in feet.');

INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (5, 1557453366, datetime('2019-05-09T22:00:00.000'), 'percentage', 5, 'Test metric record in percentage.');
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (6, 1557453426, datetime('2019-05-09T22:02:00.000'), 'percentage', 6, 'Test metric record in percentage.');
INSERT INTO records(ID, unixTime, dateTimeString, metricUnits, metricValueIDPointer, notes)
    VALUES (7, 1557453458, datetime('2019-05-09T22:02:32.000'), 'percentage', 7, 'Test metric record in percentage.');


DELETE FROM recordTagGroups;
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