import os

from flask import Flask, jsonify, request
from . import db

# http://flask.pocoo.org/docs/1.0/tutorial/database/
def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY='dev',
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, 'records.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.update(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # register the database commands
    db.init_app(app)

    @app.route('/doctors', methods=['GET'])
    def list_doctors():
        """
        Get all doctors

        :return: List of full doctor rows
        """
        cursor = db.get_db().cursor()

        result = cursor.execute(
            'SELECT id, first_name, last_name '
            'FROM doctors'
        ).fetchall()

        # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
        doctors = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        cursor.close()

        return jsonify(doctors), 200

    @app.route('/doctors/<int:doctor_id>', methods=['GET'])
    def list_doctor(doctor_id):
        """
        Get one doctor

        :param doctor_id: The id of the doctor
        :return: Full doctor row
        """
        cursor = db.get_db().cursor()

        result = cursor.execute(
            'SELECT id, first_name, last_name '
            'FROM doctors '
            'WHERE id = ?',
            (doctor_id, )
        ).fetchone()

        if result is None:
            return jsonify({'error_detail': 'Doctor not found'}), 404

        # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
        doctor = dict(zip([key[0] for key in cursor.description], result))

        cursor.close()

        return jsonify(doctor), 200

    # Note: Must set the content type to JSON. Use something like:
    # curl -X POST -H "Content-Type: application/json" --data '{"first_name": "Joe", "last_name": "Smith"}' http://localhost:5000/doctors
    @app.route('/doctors', methods=['POST'])
    def add_doctor():
        """
        Create a doctor

        :param first_name: The doctor's first name
        "param last_name: The doctor's last name

        :return: The id of the newly created doctor
        """
        req_data = request.get_json()

        try:
            first_name = req_data['first_name']
            last_name = req_data['last_name']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()

            cursor.execute(
                'INSERT INTO doctors (first_name, last_name) '
                'VALUES (?, ?)',
                (first_name, last_name)
            )

            doctor_id = cursor.lastrowid

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        return jsonify({'id': doctor_id}), 200

    @app.route('/doctors/<int:doctor_id>', methods=['DELETE'])
    def delete_doctor(doctor_id):
        """
        Delete one doctor

        :param doctor_id: The id of the doctor
        :return: True on success, False on failure
        """

        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'DELETE '
                'FROM doctors '
                'WHERE id = ?',
                (doctor_id,)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'Doctor could not be deleted'}), 404

        return jsonify({'success': True}), 200

    @app.route('/doctors/<int:doctor_id>', methods=['PUT'])
    def update_doctor(doctor_id):
        """
        Update one doctor

        :param doctor_id: The doctor's ID
        :param first_name: The doctor's first name
        :param last_name: The doctor's last name

        :return: True on success, False on failure
        """
        req_data = request.get_json()

        try:
            first_name = req_data['first_name']
            last_name = req_data['last_name']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()
            result = cursor.execute(
                'UPDATE doctors '
                'SET first_name = ?, last_name = ? '
                'WHERE id = ?',
                (first_name, last_name, doctor_id,)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'Doctor could not be updated'}), 404

        return jsonify({'success': True}), 200

    @app.route('/doctors/<int:doctor_id>/locations', methods=['GET'])
    def list_doctor_locations(doctor_id):
        """
        Get the locations for a single doctor

        :param doctor_id: The id of the doctor
        :return: List of full location rows
        """

        cursor = db.get_db().cursor()

        result = cursor.execute(
            'SELECT l.id, l.address '
            'FROM doctor_locations dl '
            'INNER JOIN locations l ON dl.location_id = l.id '
            'WHERE dl.doctor_id = ?',
            (doctor_id,)
        ).fetchall()

        if len(result) == 0:
            return jsonify({'error_detail': 'No locations found for given doctor.'}), 404

        # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
        locations = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        cursor.close()

        return jsonify(locations), 200

    @app.route('/doctors/<int:doctor_id>/locations', methods=['POST'])
    def create_doctor_locations(doctor_id):
        """
        Create a location for a given doctor

        :param doctor_id: The id of the doctor
        :param addresses: the doctor's addresses.

        :return: The list of newly created
        """
        req_data = request.get_json()

        try:
            addresses = req_data['addresses']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()

            doctor_location_id = []
            total_row_count = 0
            for address in addresses:
                cursor.execute(
                    'INSERT INTO doctor_locations (doctor_id, location_id) '
                    'SELECT ? AS doctor_id, l.id AS location_id '
                    'FROM locations l '
                    'WHERE l.address = ?',
                    (doctor_id, address,)
                )

                doctor_location_id.append(cursor.lastrowid)
                total_row_count += cursor.rowcount

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400


        if total_row_count == 0:
            return jsonify({'error_detail': 'Could not find addresses in system.'}), 404

        return jsonify({'ids': doctor_location_id}), 200

    @app.route('/doctors/<int:doctor_id>/locations/<location_id>', methods=['DELETE'])
    def delete_doctor_locations(doctor_id, location_id):
        """
        Delete a locations for a single doctor

        :param doctor_id: The id of the doctor.
        :param location_id: The id of the location.
        :return: List of full location rows
        """

        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'DELETE '
                'FROM doctor_locations '
                'WHERE doctor_id = ? AND location_id = ?',
                (doctor_id, location_id)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'Doctor could not be deleted'}), 404

        return jsonify({'success': True}), 200

    @app.route('/doctors/<int:doctor_id>/schedule', methods=['GET'])
    def list_doctor_schedule(doctor_id):
        """
        Get the schedule for the given doctor

        :param doctor_id: The id of the doctor
        :return: Full doctor row
        """
        cursor = db.get_db().cursor()

        result = cursor.execute(
            'SELECT id, doctor_id, day_enumerated, thirty_minute_time_segment '
            'FROM doctor_schedule '
            'WHERE doctor_id = ?',
            (doctor_id,)
        ).fetchall()

        if result is None:
            return jsonify({'error_detail': 'Schedule not found'}), 404

        # See https://medium.com/@PyGuyCharles/python-sql-to-json-and-beyond-3e3a36d32853
        schedule = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        cursor.close()
        print(schedule)
        return jsonify(schedule), 200

    # Note: Must set the content type to JSON. Use something like:
    # curl -X POST -H "Content-Type: application/json" --data '{"first_name": "Joe", "last_name": "Smith"}' http://localhost:5000/doctors
    @app.route('/doctors/<int:doctor_id>/schedule', methods=['POST'])
    def add_doctor_schedule(doctor_id):
        """
        Create availability in doctor's schedule

        :param week_schedule: Array of the doctor's availability.
                                We'll expect the format of this input to be:
                                [{day:<day id 0-6>, time:<time id 0-47 30 minute increments>},...]

        :return: The id of the newly created doctor
        """
        req_data = request.get_json()

        try:
            week_schedule_in_thirty_min_chunks = req_data['week_schedule']
            if len(week_schedule_in_thirty_min_chunks) == 0 \
                or not 'day' in week_schedule_in_thirty_min_chunks[0] \
                or not 'time' in week_schedule_in_thirty_min_chunks[0]:
                    raise Exception('Missing required field')
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()

            time_slot_ids = []
            for day_time in week_schedule_in_thirty_min_chunks:

                cursor.execute(
                    'INSERT INTO doctor_schedule (doctor_id, day_enumerated, thirty_minute_time_segment) '
                    'VALUES (?, ?, ?)',
                    (doctor_id, day_time['day'], day_time['time'])
                )
                time_slot_ids.append(cursor.lastrowid)

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 404

        return jsonify({'id': time_slot_ids}), 200

    @app.route('/doctors/<int:doctor_id>/schedule/day/<day_id>/time/<time_id>', methods=['DELETE'])
    def delete_doctor_schedule(doctor_id, day_id, time_id):
        """
        Delete the given time from the doctors schedule.

        :param doctor_id: The id of the doctor
        :param day_id: Id of day 0-6 0 = sunday, 6 = saturday
        :param time_id: The id of the schedule time 0-47 30 minute chunks. 0 = 00:00-00:30, 47 = 23:30-24:00
        :return: True on success, False on failure
        """

        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'DELETE '
                'FROM doctor_schedule '
                'WHERE doctor_id = ? AND day_enumerated = ? AND thirty_minute_time_segment = ?',
                (doctor_id, day_id, time_id)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'Time slot could not be delete from doctor\'s schedule.'}), 404

        return jsonify({'success': True}), 200

    @app.route('/appointments', methods=['POST'])
    def create_appointment():
        """
        Create an appointment with a doctor at one of their locations.

        :param doctor_id: The id of the doctor
        :param location_id: The id of the doctor's location
        :param time_slots: Array of the time slots you'd like to reserve for the appointment.
                            We'll expect the format of this input to be:
                            [{day:<day id 0-6>, time:<time id 0-47 30 minute increments>},...]
        :return: The appointment hash ID.
        """
        req_data = request.get_json()

        try:
            doctor_id = req_data['doctor_id']
            location_id = req_data['location_id']
            time_slots = req_data['time_slots']
            if len(time_slots) == 0 \
                    or not 'day' in time_slots[0] \
                    or not 'time' in time_slots[0]:
                raise Exception('Missing required field')

            hash_time_slots = '_'.join(['%s%s' % (t['day'], t['time']) for t in time_slots])
            appointment_hash_id = '%s%s_%s' % (doctor_id, location_id, hash_time_slots)
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()

            appointment_time_slot_ids = []
            total_row_count = 0
            for time_slot in time_slots:
                '''
                We want to insert the schedule time slots for a given doctor at a given location so
                to do this we must first narrow down our select to a selection of the given doctors
                schedule, provided that that doctor can go to the given location.
                We don't need to worry about checking whether the time slot has already been taken since this will
                be taken care of by the appointment_time_chunks table's unique constraint.
                '''
                cursor.execute(
                    'INSERT into appointment_time_chunks (appointment_hash_id, doctor_schedule_id, location_id) '
                    'SELECT ? AS appointment_hash_id, ds.id AS doctor_schedule_id, dl.location_id AS location_id '
                    'FROM doctor_schedule ds '
                    'INNER JOIN doctor_locations dl ON dl.doctor_id = ds.doctor_id '
                    'WHERE ds.doctor_id = ? AND ds.day_enumerated = ? AND ds.thirty_minute_time_segment = ? '
                    'AND dl.location_id = ? ',
                    (appointment_hash_id, doctor_id, time_slot['day'], time_slot['time'], location_id)
                )
                appointment_time_slot_ids.append(cursor.lastrowid)
                total_row_count+=cursor.rowcount

            if total_row_count != len(time_slots):
                raise Exception('Could not book appointment. Doctor is not available at the time specified.')

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        return jsonify({'appointment_hash_id': appointment_hash_id}), 200

    @app.route('/appointments', methods=['DELETE'])
    def cancel_appointment():
        """
        Cancel an appointment with a doctor at one of their locations.

        :param appointment_hash_id: The hash identification string for a patients appointment
        :return: True on success.
        """
        req_data = request.get_json()

        try:
            appointment_hash_id = req_data['appointment_hash_id']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'DELETE '
                'FROM appointment_time_chunks '
                'WHERE appointment_hash_id = ?',
                (appointment_hash_id,)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'Failed to delete appointment.'}), 404

        return jsonify({'success': True}), 200

    @app.route('/doctors/<doctor_id>/appointments', methods=['GET'])
    def get_doctors_appointments(doctor_id):
        """
        Get all appointments for the given doctor.

        :param appointment_hash_id: The hash identification string for a patients appointment
        :return: All appointments for the doctor including the hash ID and times.
        """

        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'SELECT ptc.appointment_hash_id, ds.day_enumerated, ds.thirty_minute_time_segment, l.address '
                'FROM appointment_time_chunks ptc '
                'INNER JOIN doctor_schedule ds ON ds.id = ptc.doctor_schedule_id '
                'INNER JOIN doctor_locations dl ON dl.location_id = ptc.location_id AND dl.doctor_id = ds.doctor_id '
                'INNER JOIN locations l ON l.id = dl.location_id '
                'WHERE ds.doctor_id = ?',
                (doctor_id)
            ).fetchall()

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        if result is None:
            return jsonify({'error_detail': 'Appointments not found'}), 404

        appointments = [dict(zip([key[0] for key in cursor.description], row)) for row in result]

        formatted_appointments = {}
        # previousChunk
        for apt in appointments:
            key = apt['appointment_hash_id']
            time_chunks = str(apt['thirty_minute_time_segment'])
            if key in formatted_appointments and 'time_chunks' in formatted_appointments[key]:
                time_chunks = '%s,%s' % (time_chunks, str(formatted_appointments[key]['time_chunks']))

            formatted_appointments[key] = {
                'address': apt['address'],
                'day': apt['day_enumerated'],
                'time_chunks': time_chunks
            }

        return jsonify({'appointments': formatted_appointments}), 200

    return app
