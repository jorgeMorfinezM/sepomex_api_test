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
# from flask_jwt_extended import jwt_required
from db_controller.database_backend import *
from .MunicipioModel import MunicipioModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
town_api = Blueprint('town_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


@town_api.route('/', methods=['POST', 'GET'])
# @jwt_required
def endpoint_manage_town_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:

        if request.method == 'POST':

            data = request.get_json(force=True)

            town_model = MunicipioModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT, data)

            logger.info('Data Json Municipio to Manage on DB: %s', str(data))

            town_response = town_model.insert_data(session_db, data)

            logger.info('Data Municipio to Register on DB: %s', str(data))

            if not town_response:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, town_response)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, town_response)

        elif request.method == 'GET':

            data = dict()
            towns_on_db = None

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            town_model = MunicipioModel(data)

            towns_on_db = town_model.get_all_towns(session_db, data)

            if not bool(towns_on_db) or not towns_on_db or "[]" == towns_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, towns_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, towns_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@town_api.route('/filter', methods=['GET'])
def get_looking_for_towns():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:
        data = dict()

        query_string = request.query_string.decode('utf-8')

        if request.method == 'GET':

            town_on_db = None

            filter_spec = []

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            if 'nombre_municipio' in query_string:
                town_name = request.args.get('nombre_municipio')

                data['nombre_municipio'] = town_name

                # filter_spec.append({'field': 'town_name', 'op': '==', 'value': town_name})
                filter_spec.append({'field': 'nombre_municipio', 'op': 'ilike', 'value': town_name})

            if 'clave_municipio' in query_string:
                town_key = request.args.get('clave_municipio')

                data['clave_municipio'] = town_key

                filter_spec.append({'field': 'clave_municipio', 'op': '==', 'value': town_key})

            town_model = MunicipioModel(data)

            town_on_db = town_model.get_towns_by_filters(session_db, data, filter_spec)

            if not bool(town_on_db) or not town_on_db or "[]" == town_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, town_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, town_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
