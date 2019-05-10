-- Everything here will get rolled back at the end of a test run
-- Populate everything with known data

DELETE FROM doctors;
INSERT INTO doctors(id, first_name, last_name) VALUES (0, 'Testy', 'McTestFace');
INSERT INTO doctors(id, first_name, last_name) VALUES (1, 'Julius', 'Hibbert');

DELETE FROM locations;
INSERT INTO locations(id, address) VALUES (0, '1 Park St');
INSERT INTO locations(id, address) VALUES (1, '2 University Ave');

DELETE FROM doctor_locations;
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (0, 0, 0);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (1, 0, 1);
INSERT INTO doctor_locations(id, doctor_id, location_id) VALUES (2, 1, 1);

-- For testing we're going to imagine that doctor John Doe only works on Monday from 9am till noon.
-- 9am-9:30am is 19 and 11:30am-12:00pm is 23
DELETE FROM doctor_schedule;
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (0, 0, 1, 19);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (1, 0, 1, 20);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (2, 0, 1, 21);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (3, 0, 1, 22);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (4, 0, 1, 23);
INSERT INTO doctor_schedule(id, doctor_id, day_enumerated, thirty_minute_time_segment) VALUES (5, 0, 1, 24);

-- Lets set a default appointment for doctor John Doe at 123 Main St from 9am-10am.
DELETE FROM appointment_time_chunks;
INSERT INTO appointment_time_chunks(id, appointment_hash_id, doctor_schedule_id, location_id) VALUES (0, '00_119_120', 0, 0);
INSERT INTO appointment_time_chunks(id, appointment_hash_id, doctor_schedule_id, location_id) VALUES (1, '00_119_120', 1, 0)