import json
import time

def test_create_point(client):
    # @todo add sample data here.
    rv = client.post(
        '/users/0/points',
        data=json.dumps(
            dict(
                time=time.time(),
                units='meters',
                value='1',
                notes='for testing',
                tags=['How far can I throw a base ball']
            )
        ),
        content_type='application/json'
    )
    assert rv.status_code == 200

    data = json.loads(rv.data)
    assert 'ID' in data

    rv = client.get('/users/0/points/' + str(data['ID']))
    assert rv.status_code == 200
    data = json.loads(rv.data)
    for field in ['time', 'units', 'valueInt', 'valueStr', 'valueReal', 'notes', 'tags']:
        assert field in data


def test_delete_point(client):
    rv = client.delete('/users/0/points/0')
    assert rv.status_code == 200


def test_get_point(client):
    rv = client.get('/users/0/points/0')
    data = json.loads(rv.data)
    for field in ['time', 'units', 'valueInt', 'valueStr', 'valueReal', 'notes', 'tags']:
        assert field in data
    # assert data['id'] == 0
    # assert data['firstName'] == 'John'
    # assert data['lastName'] == 'Doe'


def test_search_points(client):
    rv = client.get('/users/0/points')
    data = json.loads(rv.data)
    print(data)
    assert type(data).__name__ == 'list'
    # @todo add the data link between points and users...
    # @todo also add more tests for filtering on tags / time ranges.
    assert len(data) > 1
    for field in ['ID', 'time', 'units', 'valueInt', 'valueStr', 'valueReal', 'notes', 'tags']:
        assert field in data[0]