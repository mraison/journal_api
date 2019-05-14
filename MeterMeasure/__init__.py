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

    @app.route('/users', methods=['POST'])
    def create_user():
        req_data = request.get_json()

        try:
            firstName = req_data['firstName']
            lastName = req_data['lastName']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400


        try:
            cursor = db.get_db().cursor()

            # cursor.execute(
                # @todo add query insert here.
            # )

            # @todo add check that query was successful
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        data = {'ID': None, 'firstName': firstName, 'lastName': lastName}
        return jsonify(data), 200

    @app.route('/users/<int:userID>', methods=['GET'])
    def get_user(userID):
        try:
            cursor = db.get_db().cursor()

            # cursor.execute(
                # @todo add query insert here.
            # )

            # @todo add check that query was successful
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        data = {'ID': None, 'firstName': None, 'lastName': None}
        return jsonify(data), 200

    # Note: Must set the content type to JSON. Use something like:
    # curl -X POST -H "Content-Type: application/json" --data '{"first_name": "Joe", "last_name": "Smith"}' http://localhost:5000/doctors
    @app.route('/users/<int:userID>', methods=['PUT'])
    def update_user(userID):
        req_data = request.get_json()

        try:
            firstName = req_data['firstName']
            lastName = req_data['lastName']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400


        try:
            cursor = db.get_db().cursor()

            # result = cursor.execute(
                # @todo add query
            # )

            # @todo check query worked
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        # if result.rowcount == 0:
        #     return jsonify({'error_detail': 'User could not be updated.'}), 404

        return jsonify({}), 200

    @app.route('/users/<int:userID>', methods=['DELETE'])
    def delete_user(userID):
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()

            # result = cursor.execute(
                # @todo add query
            # )

            # @todo check query worked
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        # if result.rowcount == 0:
        #     return jsonify({'error_detail': 'User could not be deleted'}), 404

        return jsonify({}), 200

    @app.route('/users/<int:userID>/points', methods=['POST'])
    def record_point(userID):
        # @todo just return the http response
        req_data = request.get_json()

        try:
            time = req_data['time']
            units = req_data['units']
            value = req_data['value']
            notes = req_data['notes']
            tags = req_data['tags']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        try:
            cursor = db.get_db().cursor()

            # result = cursor.execute(
                # @todo add query
            # )

            # @todo check query worked
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        # if result.rowcount == 0:
        #     return jsonify({'error_detail': 'Failed to record point.'}), 404

        return jsonify({}), 200

    @app.route('/users/<int:userID>/points', methods=['GET'])
    def search_points(userID):
        # @todo return [{'time', 'units', 'value', 'notes', 'tags'}...]
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()

            # result = cursor.execute(
                # @todo add query
            # )

            # @todo check query worked
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        data = []
        return jsonify(data), 200

    @app.route('/users/<int:userID>/points/<int:pointID>', methods=['GET'])
    def get_point(userID, pointID):
        # @todo return {'time', 'units', 'value', 'notes', 'tags'}
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()

            # result = cursor.execute(
                # @todo add query
            # )

            # @todo check query worked
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        data = {'time': None, 'units': None, 'value': None, 'notes': None, 'tags': []}
        return jsonify(data), 200

    @app.route('/users/<int:userID>/points/<int:pointID>', methods=['DELETE'])
    def delete_point(userID, pointID):
        # @todo just return the http response
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()

            # result = cursor.execute(
                # @todo add query
            # )

            # @todo check query worked
        except Exception as e:
            return jsonify({'error_detail': e.message}), 400

        # if result.rowcount == 0:
        #     return jsonify({'error_detail': 'Failed to delete point.'}), 404

        return jsonify({}), 200

    return app
