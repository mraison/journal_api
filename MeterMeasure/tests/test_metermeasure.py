import json

def test_get_a_user(client):
    # Test that getting all doctors truly gets them all
    rv = client.get('/users/0')
    assert rv.status_code == 200

    # Can't guarantee order, so test that we get the expected count and fields seem to make sense
    data = json.loads(rv.data)
    assert data['id'] == 0
    assert data['firstName'] == 'John'
    assert data['lastName'] == 'Doe'


def test_get_invalid_doctor(client):
    # Test getting a single doctor that doesn't exist
    rv = client.get('/users/2')
    assert rv.status_code == 404


def test_create_user(client):
    # Test creating a real doctor, successfully

    # Note: Flask chokes if you pass in an inline dict; must use json.dumps()
    rv = client.post('/users',
                     data=json.dumps(
                         dict(
                             firstName='Elmer',
                             lastName='Hartman'
                         )
                     ),
                     content_type='application/json')

    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert data['id'] == 2


def test_create_invalid_user(client):
    # Test various ways a doctor creation may fail
    rv = client.post('/users',
                     data=json.dumps(dict(firstName='Elmer')),
                     content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'

    rv = client.post('/users',
                     data=json.dumps(dict(lastName='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 400

    data = json.loads(rv.data)
    assert data['error_detail'] == 'Missing required field'


def test_update_user(client):
    # Test creating a real doctor, successfully

    # Note: Flask chokes if you pass in an inline dict; must use json.dumps()
    rv = client.put('/users/0',
                     data=json.dumps(dict(firstName='Elmer', lastName='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 200


def test_update_invalid_user(client):
    # Test various ways a doctor creation may fail
    rv = client.put('/users/2',
                     data=json.dumps(dict(firstName='Elmer', lastName='Hartman')),
                     content_type='application/json')

    assert rv.status_code == 404

    data = json.loads(rv.data)
    assert data['error_detail'] == 'User could not be updated'


def test_delete_invalid_user(client):
    # Test deleting a single doctor that doesn't exist.
    rv = client.delete('/users/2')

    assert rv.status_code == 404


def test_delete_valid_user(client):
    # Test deleting a single doctor
    rv = client.delete('/users/0')
    assert rv.status_code == 200


def test_create_point(client):
    # @todo add sample data here.
    rv = client.post(
        '/users/0/points',
        data=json.dumps(
            dict(
                time='',
                units='',
                value='',
                notes='',
                tags=[]
            )
        ),
        content_type='application/json'
    )
    # needs to be a post
    pass


def test_delete_point(client):
    rv = client.delete('/users/0/points/0')
    assert rv.status_code == 200


def test_get_point(client):
    rv = client.get('/users/0/points/0')
    data = json.loads(rv.data)
    for field in ['time', 'units', 'value', 'notes', 'tags']:
        assert field in data
    # assert data['id'] == 0
    # assert data['firstName'] == 'John'
    # assert data['lastName'] == 'Doe'


def test_search_points(client):
    rv = client.get('/users/0/points')
    data = json.loads(rv.data)
    # @todo add the data link between points and users...
    # @todo also add more tests for filtering on tags / time ranges.
    assert len(data) > 1
    for field in ['time', 'units', 'value', 'notes', 'tags']:
        assert field in data[0]