import json

def test_get_all_doctors(client):
    # Test that getting all doctors truly gets them all
    rv = client.get('/doctors')
    assert rv.status_code == 200

    # Can't guarantee order, so test that we get the expected count and fields seem to make sense
    data = json.loads(rv.data)
    assert len(data) == 2
    for field in ['id', 'first_name', 'last_name']:
        assert field in data[0]


def test_get_valid_doctor(client):
    # Test getting a single doctor, successfully
    rv = client.get('/doctors/0')
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['id'] == 0
    assert data['first_name'] == 'Testy'
    assert data['last_name'] == 'McTestFace'


def test_get_invalid_doctor(client):
    # Test getting a single doctor that doesn't exist
    rv = client.get('/doctors/2')
    assert rv.status_code == 404


def test_create_doctor(client):
    # Test creating a real doctor, successfully

    # Note: Flask chokes if you pass in an inline dict; must use json.dumps()
    rv = client.post('/doctors',
                     data=json.dumps(dict(first_name='Elmer', last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['id'] == 2


def test_create_invalid_doctor(client):
    # Test various ways a doctor creation may fail
    rv = client.post('/doctors',
                     data=json.dumps(dict(first_name='Elmer')),
                     content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'

    rv = client.post('/doctors',
                     data=json.dumps(dict(last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'


def test_update_doctor(client):
    # Test creating a real doctor, successfully

    # Note: Flask chokes if you pass in an inline dict; must use json.dumps()
    rv = client.put('/doctors/0',
                     data=json.dumps(dict(first_name='Elmer', last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 200


def test_update_invalid_doctor(client):
    # Test various ways a doctor creation may fail
    rv = client.put('/doctors/2',
                     data=json.dumps(dict(first_name='Elmer', last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 404

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Doctor could not be updated'

    rv = client.put('/doctors/0',
                     data=json.dumps(dict(last_name='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'


def test_delete_invalid_doctor(client):
    # Test deleting a single doctor that doesn't exist.
    rv = client.delete('/doctors/2')

    assert rv.status_code == 404


def test_delete_valid_doctor(client):
    # Test deleting a single doctor
    rv = client.delete('/doctors/0')
    assert rv.status_code == 200


def test_get_doctor_locations(client):
    rv = client.get('/doctors/0/locations')
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert len(data) == 2
    for field in ['id', 'address']:
        assert field in data[0]


def test_get_invalid_doctor_locations(client):
    rv = client.get('/doctors/5/locations')
    assert rv.status_code == 404


def test_add_doctor_location(client):
    rv = client.post('/doctors/1/locations',
                     data=json.dumps(dict(addresses=['1 Park St',])),
                     content_type='application/json')
    data = json.loads(rv.data)
    print(data)

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['ids'][0] == 3


def test_add_invalid_doctor_location(client):
    rv = client.post('/doctors/1/locations',
                     data=json.dumps(dict(addresses=['123 Paper St'])),
                     content_type='application/json')
    assert rv.status_code == 404

    rv = client.post('/doctors/1/locations',
                     data=json.dumps(dict()),
                     content_type='application/json')
    assert rv.status_code == 400
    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'


def test_delete_doctor_location(client):
    rv = client.delete('/doctors/0/locations/1')
    assert rv.status_code == 200


def test_delete_doctor_location(client):
    rv = client.delete('/doctors/1/locations/0')
    assert rv.status_code == 404


def test_get_doctor_schedule(client):
    rv = client.get('/doctors/0/schedule')
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert len(data) == 6
    for field in ['id', 'doctor_id', 'day_enumerated', 'thirty_minute_time_segment']:
        assert field in data[0]


def test_add_doctor_schedule_time_slot(client):
    ## lets add an extra hour to this doctor's day.
    rv = client.post('/doctors/0/schedule',
                     data=json.dumps(dict(week_schedule=[{'day':1, 'time':25}, {'day':1, 'time':26}])),
                     content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    ## check the number of new ids generated
    assert len(data['id']) == 2
    ## check that the values of the ideas are what we expect.
    assert data['id'][0] == 6
    assert data['id'][1] == 7


def test_remove_doctor_schedule_time_slot(client):
    ## lets now remove the last time slot so the doctor can leave a little early.
    rv = client.delete('/doctors/0/schedule/day/1/time/23')
    assert rv.status_code == 200


def test_create_appointment(client):
    ## lets make an appointment for 10am-12pm on monday.
    ## we'll book it with doctor John Doe at 123 Main St
    rv = client.post('/appointments',
                     data=json.dumps(dict(
                         time_slots=[
                             {'day': 1, 'time': 21},
                             {'day': 1, 'time': 22},
                             {'day': 1, 'time': 23},
                             {'day': 1, 'time': 24}
                         ],
                         doctor_id=0,
                         location_id=0
                     )),
                     content_type='application/json')

    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'appointment_hash_id' in data
    assert data['appointment_hash_id'] != ''


def test_create_invalid_appointment(client):
    ## try to book appointment at a location the doctor is not available at.
    rv = client.post('/appointments',
                     data=json.dumps(dict(
                         time_slots=[
                             {'day': 1, 'time': 21},
                             {'day': 1, 'time': 22},
                             {'day': 1, 'time': 23},
                             {'day': 1, 'time': 24}
                         ],
                         doctor_id=0,
                         location_id=5
                     )),
                     content_type='application/json')
    data = json.loads(rv.data)
    assert rv.status_code == 400
    assert data['error_detail'] == 'Could not book appointment. Doctor is not available at the time specified.'

    ## try to book a doctor that doesn't exist.
    rv = client.post('/appointments',
                     data=json.dumps(dict(
                         time_slots=[
                             {'day': 1, 'time': 21},
                             {'day': 1, 'time': 22},
                             {'day': 1, 'time': 23},
                             {'day': 1, 'time': 24}
                         ],
                         doctor_id=2,
                         location_id=0
                     )),
                     content_type='application/json')
    data = json.loads(rv.data)
    assert rv.status_code == 400
    assert data['error_detail'] == 'Could not book appointment. Doctor is not available at the time specified.'

    ## try to book a time not fully on the doctors schedule.
    rv = client.post('/appointments',
                     data=json.dumps(dict(
                         time_slots=[
                             {'day': 1, 'time': 22},
                             {'day': 1, 'time': 23},
                             {'day': 1, 'time': 24},
                             {'day': 1, 'time': 25}
                         ],
                         doctor_id=0,
                         location_id=0
                     )),
                     content_type='application/json')
    data = json.loads(rv.data)
    assert rv.status_code == 400
    assert data['error_detail'] == 'Could not book appointment. Doctor is not available at the time specified.'

    ## try booking an appointment at the same time as another appointment.
    rv = client.post('/appointments',
                     data=json.dumps(dict(
                         time_slots=[
                             {'day': 1, 'time': 20},
                             {'day': 1, 'time': 21}
                         ],
                         doctor_id=0,
                         location_id=0
                     )),
                     content_type='application/json')
    assert rv.status_code == 400


def test_canceling_an_appointment(client):
    rv = client.delete('/appointments',
                       data=json.dumps(dict(appointment_hash_id='00_119_120')),
                       content_type='application/json')
    assert rv.status_code == 200


def test_get_doctors_appointments(client):
    # We're expecting the following as a return
    # {
    #   "appointments": {
    #     "00_119_120": {
    #       "address": "123 Main St",
    #       "day": 1,
    #       "time_chunks": "20,19"
    #     }
    #   }
    # }
    rv = client.get('/doctors/0/appointments')

    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert 'appointments' in data
    assert '00_119_120' in data['appointments']
    assert 'address' in data['appointments']['00_119_120']
    assert 'day' in data['appointments']['00_119_120']
    assert 'time_chunks' in data['appointments']['00_119_120']