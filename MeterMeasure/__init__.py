import os

from flask import Flask, jsonify, request, abort
from flask_cors import CORS
import sys
import urllib.parse
import re
from . import db
import click

from .shared.middleware.jwt import check_jwt
from .shared.configs.serviceConsts import SECRET

JWT_SECRET = SECRET

## defining additional middleware:
from functools import wraps

def verify_user():
    def decorator(f):
        @wraps(f)
        def decorated_function(jwt_body, userID, *args, **kws):
            if not jwt_body['ID'] == userID:
                abort(401)

            return f(userID, *args, **kws)
        return decorated_function
    return decorator

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

def choose_between_value_types(
        intVal,
        floatVal,
        stringVal
):
    if intVal:
        return intVal
    if floatVal:
        return floatVal
    if stringVal:
        return stringVal

# http://flask.pocoo.org/docs/1.0/tutorial/database/
def create_app(test_config=None):
    """Create and configure an instance of the Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        # a default secret that should be overridden by instance config
        SECRET_KEY=JWT_SECRET,
        # store the database in the instance folder
        DATABASE=os.path.join(app.instance_path, 'records.sqlite')

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

    cors = CORS(app, origins='*',
        headers=['Content-Type', 'Authorization'],
        expose_headers=['Content-Type', 'Authorization'])

    @app.route('/users/<int:userID>/recordSets', methods=['POST'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def create_record_set(userID):
        req_data = request.get_json()

        try:
            name = req_data['name']
            recSetPermGroupName = req_data['permissionGroupName']
            ownerPermissions = 'rw'
            groupPermissions = req_data['groupPermissionsActions']
            allPermissions = req_data['globalPermissionsActions']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        ############################
        #    Function specific stuff start.
        ############################
        # cast values to record

        try:
            cursor = db.get_db().cursor()
            recordresult = cursor.execute(
                'INSERT INTO recordSet (name, userID, recSetPermGroupName, ownerPermissions, groupPermissions, allPermissions) '
                'VALUES(?, ?, ?, ?, ?, ?)',
                (name, userID, recSetPermGroupName, ownerPermissions, groupPermissions, allPermissions)
            )
            recordSetID = recordresult.lastrowid

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if recordresult.rowcount == 0:
            return jsonify({'error_detail': 'Failed to delete point.'}), 504

        data = {
            'ID': recordSetID,
        }
        return jsonify(data), 200

    @app.route('/users/<int:userID>/recordSets', methods=['GET'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def get_all_record_sets(userID):
        try:
            cursor = db.get_db().cursor()
            results = cursor.execute(
                'SELECT * FROM recordSet '
                'WHERE userID = ? ',
                (userID,)
            ).fetchall()

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        data = [dict(zip([key[0] for key in cursor.description], row)) for row in results]
        if len(data) == 0:
            return jsonify({'error_detail': 'No points found'}), 404

        return jsonify(data), 200

    @app.route('/users/<int:userID>/recordSets/<int:recordSetID>', methods=['GET'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def get_record_set(userID, recordSetID):
        try:
            cursor = db.get_db().cursor()
            results = cursor.execute(
                'SELECT * FROM recordSet '
                'WHERE ID = ? AND userID = ? ',
                (recordSetID, userID)
            ).fetchall()

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        data = [dict(zip([key[0] for key in cursor.description], row)) for row in results]
        if len(data) == 0:
            return jsonify({'error_detail': 'No points found'}), 404

        return jsonify(data), 200

    @app.route('/users/<int:userID>/recordSets/<int:recordSetID>', methods=['PUT'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def update_record_set(userID, recordSetID):
        req_data = request.get_json()

        try:
            name = req_data['name']
            recSetPermGroupName = req_data['permissionGroupName']
            groupPermissions = req_data['groupPermissionsActions']
            allPermissions = req_data['globalPermissionsActions']
        except KeyError:
            return jsonify({'error_detail': 'Missing required field'}), 400

        ############################
        #    Function specific stuff start.
        ############################
        # cast values to record

        try:
            cursor = db.get_db().cursor()
            recordresult = cursor.execute(
                'UPDATE recordSet '
                'SET name = ?, '
                'recSetPermGroupName = ?, '
                'groupPermissions = ?, '
                'allPermissions = ? '
                'WHERE ID = ? AND userID = ? ',
                (name, recSetPermGroupName, groupPermissions, allPermissions, recordSetID, userID)
            )

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        if recordresult.rowcount == 0:
            return jsonify({'error_detail': 'No record set found.'}), 404

        return jsonify(), 200

    @app.route('/users/<int:userID>/recordSets/<int:recordSetID>/measurements', methods=['GET'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def get_measurements(userID, recordSetID):
        ## MeasurementID will be unique across the whole database so we can just do a simple select on the measurement table.
        ## No need for joining on the record set other than to esnure user's don't try to grab points from other sets off this endpoint.
        try:
            cursor = db.get_db().cursor()
            results = cursor.execute(
                'SELECT m.* FROM measurements m '
                'inner join joinMeasurementsToRecordSet mjr on m.ID = mjr.measurementsID '
                'inner join recordSet r ON mjr.recordSetID = r.ID '
                'WHERE r.ID = ?',
                (recordSetID,)
            ).fetchall()

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        data = [dict(zip([key[0] for key in cursor.description], row)) for row in results]
        if len(data) == 0:
            return jsonify({'error_detail': 'No points found'}), 404

        def df(d):
            d['value'] = choose_between_value_types(d['intVal'], d['floatVal'], d['strVal'])
            return d

        response_data = [df(d) for d in data]

        return jsonify(response_data), 200

    @app.route('/users/<int:userID>/recordSets/<int:recordSetID>/measurements', methods=['POST'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def record_measurement(userID, recordSetID):
        # print(request, file=sys.stderr)
        # print(request, file=sys.stdout)
        # @todo just return the http response
        req_data = request.get_json()

        try:
            time = req_data['time']   # int
            units = req_data['units'] # string
            value = req_data['value'] # mixed
            notes = req_data['notes'] # string
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
            recordresult = cursor.execute(
                'INSERT INTO measurements (unixTime, units, intVal, strVal, floatVal, notes) '
                'VALUES(?, ?, ?, ?, ?, ?)',
                (int(time), units, valueInt, valueString, valueReal, notes,)
            )
            pointID = recordresult.lastrowid

            if recordresult.rowcount == 0:
                return jsonify({'error_detail': 'Failed to create measurement'}), 504

            joinResult = cursor.execute(
                'INSERT INTO joinMeasurementsToRecordSet (recordSetID, measurementsID) '
                'VALUES(?, ?)',
                (recordSetID, pointID,)
            )

            if joinResult.rowcount == 0:
                return jsonify({'error_detail': 'Failed to add measurement to record set. Disjoint measurement created: ID - %s.' % pointID}), 504

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400
        ############################
        #    Function specific stuff end.
        ############################

        data = {
            'ID': pointID,
        }
        return jsonify(data), 200


    @app.route('/users/<int:userID>/recordSets/<int:recordSetID>/measurements/<int:measurementID>', methods=['GET'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def get_measurement(userID, recordSetID, measurementID):
        ## MeasurementID will be unique across the whole database so we can just do a simple select on the measurement table.
        ## No need for joining on the record set other than to esnure user's don't try to grab points from other sets off this endpoint.
        try:
            cursor = db.get_db().cursor()
            results = cursor.execute(
                'SELECT m.* FROM measurements m '
                'inner join joinMeasurementsToRecordSet mjr on m.ID = mjr.measurementsID '
                'inner join recordSet r ON mjr.recordSetID = r.ID '
                'WHERE r.ID = ? AND m.ID = ? ',
                (recordSetID, measurementID,)
            ).fetchall()

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        data = [dict(zip([key[0] for key in cursor.description], row)) for row in results]
        if len(data) == 0:
            return jsonify({'error_detail': 'No points found'}), 404

        return jsonify(data[0]), 200

    ## @todo This is the last bit for the api. I need to decide who own's a point and whether, after delete,
    # it should be included in anyone elses groups...Initially I think it's safe to say no.
    @app.route('/users/<int:userID>/recordSets/<int:recordSetID>/measurements/<int:measurementID>', methods=['DELETE'])
    @check_jwt(app.config['SECRET_KEY'])
    @verify_user()
    def delete_point(userID, recordSetID, measurementID):
        # @todo just return the http response
        # @todo just return the http response
        try:
            cursor = db.get_db().cursor()
            result = cursor.execute(
                'DELETE FROM measurements '
                'WHERE ID = ?'
                ,
                (measurementID,)
            )
            if result.rowcount == 0:
                return jsonify({'error_detail': 'Failed to delete point.'}), 504

            result = cursor.execute(
                'DELETE FROM joinMeasurementsToRecordSet '
                'WHERE measurementsID = ? AND recordSetID = ?'
                ,
                (measurementID, recordSetID,)
            )
            if result.rowcount == 0:
                return jsonify({'error_detail': 'Failed to null pointer from record set.'}), 504

            db.get_db().commit()
            cursor.close()
        except Exception as e:
            return jsonify({'error_detail': str(e)}), 400

        return jsonify({}), 200

    # @app.route('/users/<int:userID>/points', methods=['GET'])
    # @check_jwt(app.config['SECRET_KEY'])
    # @verify_user()
    # def search_points(userID, recordSetID):
    #     tagsInput = request.args.get('tags')
    #     tags = urllib.parse.unquote(tagsInput) if not tagsInput is None else None ## .split(',')
    #     click.echo(tags)
    #     timeStart = request.args.get('timeStart')
    #     timeEnd = request.args.get('timeEnd')
    #     tagWhereClause = ''
    #     if tags:
    #         # tagWhereClause = 'AND (\'' + tags + '\' LIKE \'%\' + rtg.name + \'%\' ) '
    #         tagWhereClause = 'AND (\'' + tags + '\' LIKE rtg.name) '
    #         click.echo(tagWhereClause)
    #
    #     timeWhereClause = ''
    #     if timeStart and timeEnd:
    #         timeWhereClause = 'AND (m.unixTime >= ' + str(timeStart) + ' AND m.unixTime <= ' + str(timeEnd) + ') '
    #
    #     try:
    #         cursor = db.get_db().cursor()
    #         result = cursor.execute(
    #             'SELECT '
    #             '   m.ID as ID, '
    #             '   m.unixTime AS time, '
    #             '   m.units AS units, '
    #             '   m.intVal AS valueInt, '
    #             '   m.strVal AS valueStr, '
    #             '   m.floatVal AS valueReal, '
    #             '   m.notes AS notes, '
    #             '   Group_Concat(rtg.name, \',\') AS tags '
    #             'FROM measurements m '
    #             'INNER JOIN joinMeasurementsToRecordSet jmrs ON m.ID = jmrs.measurementsID '
    #             'INNER JOIN recordSet rtg ON jmrs.recordSetID = rtg.ID '
    #             'INNER JOIN recordSetPermissionGroups rspg ON rtg.recSetPermGroupName = rspg.name '
    #             'WHERE rspg.userID = ? '
    #             '%s '
    #             '%s '
    #             'GROUP BY '
    #             '   m.unixTime, '
    #             '   m.units, '
    #             '   m.intVal, '
    #             '   m.strVal, '
    #             '   m.floatVal, '
    #             '   m.notes' % (tagWhereClause, timeWhereClause),
    #             (userID,)
    #         ).fetchall()
    #
    #         cursor.close()
    #     except Exception as e:
    #         return jsonify({'error_detail': str(e)}), 400
    #
    #     data = [dict(zip([key[0] for key in cursor.description], row)) for row in result]
    #     if len(data) == 0:
    #         return jsonify({'error_detail': 'No points found'}), 404
    #
    #     def df(d):
    #         d['value'] = choose_between_value_types(d['valueInt'], d['valueReal'], d['valueStr'])
    #         return d
    #
    #     response_data = [df(d) for d in data]
    #
    #     return jsonify(response_data), 200

    return app
