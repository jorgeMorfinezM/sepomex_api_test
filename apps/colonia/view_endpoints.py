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
from .ColoniaModel import ColoniaModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *
from datetime import datetime

cfg_app = get_config_settings_app()
suburb_api = Blueprint('suburb_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


@suburb_api.route('/', methods=['POST', 'GET'])
# @jwt_required
def endpoint_manage_suburb_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:

        if request.method == 'POST':

            data = request.get_json(force=True)

            suburb_model = ColoniaModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT, data)

            logger.info('Data Json Ciudad to Manage on DB: %s', str(data))

            suburb_response = suburb_model.insert_data(session_db, data)

            logger.info('Data Ciudad to Register on DB: %s', str(data))

            if not suburb_response:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, suburb_response)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, suburb_response)

        elif request.method == 'GET':

            data = dict()
            suburb_on_db = None

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            suburb_model = ColoniaModel(data)

            suburb_on_db = suburb_model.get_all_suburbs(session_db, data)

            if not bool(suburb_on_db) or not suburb_on_db or "[]" == suburb_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, suburb_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, suburb_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@suburb_api.route('/filter', methods=['GET'])
def get_looking_for_suburbs():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:
        data = dict()

        query_string = request.query_string.decode('utf-8')

        if request.method == 'GET':

            suburb_on_db = None

            filter_spec = []

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            if 'nombre_colonia' in query_string:
                suburb_name = request.args.get('nombre_colonia')

                data['nombre_colonia'] = suburb_name

                filter_spec.append({'field': 'nombre_colonia', 'op': 'ilike', 'value': suburb_name})

            if 'codigo_postal' in query_string:
                zip_postal_code = request.args.get('codigo_postal')

                data['codigo_postal'] = zip_postal_code

                filter_spec.append({'field': 'codigo_postal', 'op': '==', 'value': zip_postal_code})

            suburb_model = ColoniaModel(data)

            suburb_on_db = suburb_model.get_suburbs_by_filters(session_db, data, filter_spec)

            if not bool(suburb_on_db) or not suburb_on_db or "[]" == suburb_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, suburb_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, suburb_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
