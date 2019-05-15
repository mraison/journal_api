import os

from flask import Flask, jsonify, request
import re
from . import db

###################
# I'm just going to toss this utility down here.
###################
def _get_point_value_type(value):
    v = str(value)
    if not re.match('^\d+$', v) is None:
        return 'int'
    if not re.match('^\d+\.\d+$', v) is None:
        return 'float'
    return 'string'

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
            firstName = req_data["firstName"]
            lastName = req_data["lastName"]
            id = None
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400


        try:
            cursor = db.get_db().cursor()

            cursor.execute(
                'INSERT INTO users (firstName, lastName) '
                'Values(?, ?)',
                (firstName, lastName,)
            )
            id = cursor.lastrowid
            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        data = {'ID': id, 'firstName': firstName, 'lastName': lastName}
        return jsonify(data), 200

    @app.route('/users/<int:userID>', methods=['GET'])
    def get_user(userID):
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'SELECT ID, firstName, lastName '
                'FROM users '
                'WHERE ID = ?',
                (userID,)
            ).fetchone()
            cursor.close()

            # @todo add check that query was successful
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if result is None:
            return jsonify({'error_detail': 'User not found'}), 404

        data = dict(zip([key[0] for key in cursor.description], result))

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

            result = cursor.execute(
                'UPDATE users '
                'SET firstName = ?, lastName = ? '
                'WHERE ID = ?',
                (firstName, lastName, userID)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'User could not be updated.'}), 404

        return jsonify({}), 200

    @app.route('/users/<int:userID>', methods=['DELETE'])
    def delete_user(userID):
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                # @todo add query
                'DELETE FROM users '
                'WHERE ID = ?',
                (userID,)
            )

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'User could not be deleted'}), 404

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
            tags.append(None) ## ensure the null group exists
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        ############################
        #    Function specific stuff start.
        ############################
        # cast values to record
        valueInt = None
        valueString = None
        valueReal = None
        inputValType = _get_point_value_type(value)
        if inputValType == 'int':
            valueInt = int(value)
        elif inputValType == 'float':
            valueReal = float(value)
        else:
            valueString = str(value)

        try:
            cursor = db.get_db().cursor()
            valresult = cursor.execute(
                'INSERT INTO recordValueStore (intVal, strVal, floatVal) '
                'VALUES(?, ?, ?)',
                (valueInt, valueString, valueReal,)
            )
            valueID = valresult.lastrowid
            db.get_db().commit()

            recordresult = cursor.execute(
                'INSERT INTO records (unixTime, metricUnits, metricValueIDPointer, notes) '
                'VALUES(?, ?, ?, ?)',
                (int(time), units, valueID, notes,)
            )
            recordID = recordresult.lastrowid
            db.get_db().commit()

            tagUpdates = []
            for tag in enumerate(tags):
                tagResults = cursor.execute(
                    'INSERT INTO recordTagGroups (tagGroupName, userID, recordIDPointer) '
                    'VALUES(?, ?, ?)',
                    (str(tag), userID, recordID,)
                )
                tagUpdates.append(tagResults.lastrowid)

            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400
        ############################
        #    Function specific stuff end.
        ############################

        if len(tagUpdates) == 0:
            return jsonify({'error_detail': 'Failed to record point.'}), 404

        data = {
            'ID': valueID
        }
        return jsonify(data), 200

    @app.route('/users/<int:userID>/points', methods=['GET'])
    def search_points(userID):
        tagsInput = request.args.get('tags')
        tags = tagsInput.split(',') if not tagsInput is None else None
        timeStart = request.args.get('timeStart')
        timeEnd = request.args.get('timeEnd')
        tagWhereClause = ''
        if tags:
            tagWhereClause = 'AND (rtg.tagGroupName LIKE \'' + '\' OR rtg.tagGroupName LIKE \''.join(tags) + '\') '

            # return jsonify(tagWhereClause), 200
        timeWhereClause = ''
        if timeStart and timeEnd:
            timeWhereClause = 'AND (r.unixTime >= ' + str(timeStart) + ' AND r.unixTime <= ' + str(timeEnd) + ') '

        try:
            cursor = db.get_db().cursor()
            result = cursor.execute(
                'SELECT '
                '   rvs.ID as ID, '
                '   r.unixTime AS time, '
                '   r.metricUnits AS units, '
                '   rvs.intVal AS valueInt, '
                '   rvs.strVal AS valueStr, '
                '   rvs.floatVal AS valueReal, '
                '   r.notes AS notes, '
                '   Group_Concat(rtg.tagGroupName) AS tags '
                'FROM recordValueStore rvs '
                'INNER JOIN records r ON rvs.ID = r.metricValueIDPointer '
                'INNER JOIN recordTagGroups rtg ON r.ID = rtg.recordIDPointer '
                'WHERE rtg.userID = ? '
                '%s '
                '%s '
                'GROUP BY '
                '   r.unixTime, '
                '   r.metricUnits, '
                '   rvs.intVal, '
                '   rvs.strVal, '
                '   rvs.floatVal, '
                '   r.notes' % (tagWhereClause, timeWhereClause),
                (userID,)
            ).fetchall()

            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        data = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
        if len(data) == 0:
            return jsonify({'error_detail': 'No points found'}), 404

        return jsonify(data), 200

    @app.route('/users/<int:userID>/points/<int:pointID>', methods=['GET'])
    def get_point(userID, pointID):
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'SELECT '
                '   rvs.ID as ID, '
                '   r.unixTime AS time, '
                '   r.metricUnits AS units, '
                '   rvs.intVal AS valueInt, '
                '   rvs.strVal AS valueStr, '
                '   rvs.floatVal AS valueReal, '
                '   r.notes AS notes, '
                '   Group_Concat(rtg.tagGroupName) AS tags '
                'FROM recordValueStore rvs '
                'INNER JOIN records r ON rvs.ID = r.metricValueIDPointer '
                'INNER JOIN recordTagGroups rtg ON r.ID = rtg.recordIDPointer '
                'WHERE rtg.userID = ? AND rvs.ID = ? '
                'GROUP BY '
                '   r.unixTime, '
                '   r.metricUnits, '
                '   rvs.intVal, '
                '   rvs.strVal, '
                '   rvs.floatVal, '
                '   r.notes',
                (userID, pointID,)
            ).fetchone()

            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if result is None:
            return jsonify({'error_detail': 'Point not found'}), 404

        data = dict(zip([key[0] for key in cursor.description], result))
        return jsonify(data), 200

    ## @todo This is the last bit for the api. I need to decide who own's a point and whether, after delete,
    # it should be included in anyone elses groups...Initially I think it's safe to say no.
    @app.route('/users/<int:userID>/points/<int:pointID>', methods=['DELETE'])
    def delete_point(userID, pointID):
        # @todo just return the http response
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()

            result = cursor.execute(
                'WITH record_set as ( '
                '   SELECT DISTINCT rtg.ID as rtg_id ' ## , r.ID as r_id, rvs.ID as rvs_id
                '   FROM recordTagGroups rtg '
                '   INNER JOIN records r ON rtg.recordIDPointer = r.ID '
                '   INNER JOIN recordValueStore rvs ON r.metricValueIDPointer = rvs.ID '
                '   WHERE rtg.userID = ? AND rvs.ID = ? '
                ') '
                'DELETE FROM recordTagGroups '
                'WHERE ID in (SELECT rtg_id FROM record_set);'
                ,
                (userID, pointID,)
            )
            # cursor.close()
            db.get_db().commit()

            result = cursor.execute(
                'WITH record_set as ( '
                '   SELECT DISTINCT r.ID as r_id '
                '   FROM records r '
                '   INNER JOIN recordValueStore rvs ON r.metricValueIDPointer = rvs.ID '
                '   WHERE rvs.ID = ? '
                ') '
                'DELETE FROM records '
                'WHERE ID in (SELECT r_id FROM record_set);'
                ,
                (pointID,)
            )
            db.get_db().commit()

            result = cursor.execute(
                'WITH record_set as ( '
                '   SELECT DISTINCT rvs.ID as rvs_id'
                '   FROM recordValueStore rvs '
                '   WHERE rvs.ID = ? '
                ') '
                'DELETE FROM recordValueStore '
                'WHERE ID in (SELECT rvs_id FROM record_set);'
                ,
                (pointID,)
            )
            cursor.close()
            db.get_db().commit()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if result.rowcount == 0:
            return jsonify({'error_detail': 'Failed to delete point.'}), 404

        return jsonify({}), 200

    return app
