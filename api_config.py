# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.H05.1 ($Rev: 2 $)"

import threading
import time
from flask import Flask
from flask_jwt_extended import JWTManager
from apps.api_authentication.view_endpoints import authorization_api
from apps.estado.view_endpoints import state_api
from apps.municipio.view_endpoints import town_api
from apps.ciudad.view_endpoints import city_api
from apps.colonia.view_endpoints import suburb_api
from utilities.Utility import *

cfg_db = get_config_settings_db()
cfg_app = get_config_settings_app()


def create_app():
    app_api = Flask(__name__, static_url_path='/static')

    app_api.config['JWT_SECRET_KEY'] = cfg_app.api_key.__str__()
    app_api.config['JWT_BLACKLIST_ENABLED'] = cfg_app.jwt_blacklist_enabled
    app_api.config['JWT_BLACKLIST_TOKEN_CHECKS'] = cfg_app.jwt_blacklist_token_check
    app_api.config['JWT_ERROR_MESSAGE_KEY'] = cfg_app.jwt_error_message.__str__()
    app_api.config['JWT_ACCESS_TOKEN_EXPIRES'] = cfg_app.jwt_access_token_expires
    app_api.config['PROPAGATE_EXCEPTIONS'] = cfg_app.jwt_propagate_exceptions

    if not 'development' == cfg_app.flask_api_env:
        app_api.config['SQLALCHEMY_DATABASE_URI'] = cfg_db.Production.SQLALCHEMY_DATABASE_URI.__str__()

    app_api.config['SQLALCHEMY_DATABASE_URI'] = cfg_db.Development.SQLALCHEMY_DATABASE_URI.__str__()

    # USER
    app_api.register_blueprint(authorization_api, url_prefix='/api/v1/manager/sepomex/')

    # STATE
    app_api.register_blueprint(state_api, url_prefix='/api/v1/manager/sepomex/estado')

    # TOWN
    app_api.register_blueprint(town_api, url_prefix='/api/v1/manager/sepomex/municipio')

    # CITY
    app_api.register_blueprint(city_api, user_role_api='/api/v1/manager/sepomex/ciudad')

    # SUBURB
    app_api.register_blueprint(suburb_api, url_prefix='/api/v1/manager/sepomex/colonia')

    jwt_manager = JWTManager(app_api)

    jwt_manager.init_app(app_api)

    return app_api
