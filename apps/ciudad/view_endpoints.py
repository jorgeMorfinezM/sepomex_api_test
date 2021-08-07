# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.H05.1 ($Rev: 2 $)"

from flask import Blueprint, json, request
from flask_jwt_extended import jwt_required
from db_controller.database_backend import *
from .CiudadModel import CiudadModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
city_api = Blueprint('city_api', __name__, url_prefix='/role')
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


@city_api.route('/', methods=['POST', 'GET'])
@jwt_required
def endpoint_manage_city_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:

        if request.method == 'POST':

            data = request.get_json(force=True)

            city_model = CiudadModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT, data)

            logger.info('Data Json Ciudad to Manage on DB: %s', str(data))

            town_response = city_model.insert_data(session_db, data)

            logger.info('Data Ciudad to Register on DB: %s', str(data))

            if not town_response:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, town_response)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, town_response)

        elif request.method == 'GET':

            data = dict()
            city_on_db = None

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            city_model = CiudadModel(data)

            city_on_db = city_model.get_all_cities(session_db, data)

            if not bool(city_on_db) or not city_on_db or "[]" == city_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, city_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, city_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@city_api.route('/filter', methods=['GET'])
@jwt_required
def get_looking_for_cities():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:
        data = dict()

        query_string = request.query_string.decode('utf-8')

        if request.method == 'GET':

            city_on_db = None

            filter_spec = []

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            if 'nombre_ciudad' in query_string:
                city_name = request.args.get('nombre_ciudad')

                data['nombre_ciudad'] = city_name

                filter_spec.append({'field': 'nombre_ciudad', 'op': 'ilike', 'value': city_name})

            if 'clave_ciudad' in query_string:
                city_key = request.args.get('clave_ciudad')

                data['clave_ciudad'] = city_key

                filter_spec.append({'field': 'clave_ciudad', 'op': '==', 'value': city_key})

            city_model = CiudadModel(data)

            city_on_db = city_model.get_cities_by_filters(session_db, data, filter_spec)

            if not bool(city_on_db) or not city_on_db or "[]" == city_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, city_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, city_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
