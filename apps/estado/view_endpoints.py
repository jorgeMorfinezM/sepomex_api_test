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
from .EstadoModel import EstadoModel
from handler_controller.ResponsesHandler import ResponsesHandler as HandlerResponse
from handler_controller.messages import SuccessMsg, ErrorMsg
from logger_controller.logger_control import *
from utilities.Utility import *

cfg_app = get_config_settings_app()
state_api = Blueprint('state_api', __name__)
# jwt = JWTManager(bancos_api)
logger = configure_logger('ws')


@state_api.route('/', methods=['POST', 'GET'])
# @jwt_required
def endpoint_manage_state_data():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:

        if request.method == 'POST':

            data = request.get_json(force=True)

            state_model = EstadoModel(data)

            if not data or str(data) is None:
                return HandlerResponse.request_conflict(ErrorMsg.ERROR_REQUEST_DATA_CONFLICT, data)

            logger.info('Data Json Estado to Manage on DB: %s', str(data))

            state_response = state_model.insert_data(session_db, data)

            logger.info('Data Estado to Register on DB: %s', str(data))

            if not state_response:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, state_response)

            return HandlerResponse.response_resource_created(SuccessMsg.MSG_CREATED_RECORD, state_response)

        elif request.method == 'GET':
            data = dict()
            states_on_db = None

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            state_model = EstadoModel(data)

            states_on_db = state_model.get_all_states(session_db, data)

            if not bool(states_on_db) or not states_on_db or "[]" == states_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, states_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, states_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)


@state_api.route('/filter', methods=['GET'])
def get_looking_for_state():
    conn_db, session_db = init_db_connection()

    headers = request.headers
    auth = headers.get('Authorization')

    if not auth and 'Bearer' not in auth:
        return HandlerResponse.request_unauthorized(ErrorMsg.ERROR_REQUEST_UNAUTHORIZED, auth)
    else:
        data = dict()

        query_string = request.query_string.decode('utf-8')

        if request.method == 'GET':

            state_on_db = None

            filter_spec = []

            data['offset'] = request.args.get('offset', 1)
            data['limit'] = request.args.get('limit', 10)

            if 'nombre_estado' in query_string:
                state_name = request.args.get('nombre_estado')

                data['nombre_estado'] = state_name

                # filter_spec.append({'field': 'state_name', 'op': '==', 'value': state_name})
                filter_spec.append({'field': 'nombre_estado', 'op': 'ilike', 'value': state_name})

            if 'clave_estado' in query_string:
                state_key = request.args.get('clave_estado')

                data['clave_estado'] = state_key

                filter_spec.append({'field': 'clave_estado', 'op': '==', 'value': state_key})

            state_model = EstadoModel(data)

            state_on_db = state_model.get_states_by_filters(session_db, data, filter_spec)

            if not bool(state_on_db) or not state_on_db or "[]" == state_on_db:
                return HandlerResponse.response_success(ErrorMsg.ERROR_DATA_NOT_FOUND, state_on_db)

            return HandlerResponse.response_success(SuccessMsg.MSG_GET_RECORD, state_on_db)

        else:
            return HandlerResponse.request_not_found(ErrorMsg.ERROR_METHOD_NOT_ALLOWED)
