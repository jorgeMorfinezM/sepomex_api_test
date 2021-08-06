# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later
"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.H05.1 ($Rev: 2 $)"

import os
from os.path import join, dirname
from dotenv import load_dotenv


class Constants:
    def __init__(self):
        # Create .env_temp file path.
        dotenv_path = join(dirname(__file__), '.env')

        # Load file from the path.
        load_dotenv(dotenv_path)

    class Development(object):
        """
        Development environment configuration
        """
        DEBUG = True
        TESTING = True
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')

    class Production(object):
        """
        Production environment configurations
        """
        DEBUG = False
        TESTING = False
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class AppConstants(Constants):

    log_file_apply = bool()
    log_types = list()
    log_file_extension = str()
    log_file_app_name = str()
    log_file_save_path = str()
    flask_api_debug = str()
    flask_api_env = str()
    flask_api_port = int()
    app_config = {}
    date_timezone = str()
    api_key = str()
    jwt_blacklist_enabled = bool()      # JWT_BLACKLIST_ENABLED = False
    jwt_blacklist_token_check = list()  # JWT_BLACKLIST_TOKEN_CHECKS = ['access', 'refresh']
    jwt_error_message = str()           # JWT_ERROR_MESSAGE_KEY = 'message'
    jwt_access_token_expires = int()    # JWT_ACCESS_TOKEN_EXPIRES = 3600
    jwt_propagate_exceptions = bool()   # PROPAGATE_EXCEPTIONS = True

    def __init__(self):
        super().__init__()

        app_config = {
            'development': Constants.Development,
            'production': Constants.Production,
        }

        self.log_file_apply = os.getenv('APPLY_LOG_FILE')
        self.log_types = os.getenv('LOGGER_TYPES')
        self.log_file_extension = os.getenv('FILE_LOG_EXTENSION')
        self.log_file_app_name = os.getenv('APP_FILE_LOG_NAME')
        self.log_file_save_path = os.getenv('DIRECTORY_LOG_FILES')
        self.app_config = app_config
        self.flask_api_debug = os.getenv('FLASK_DEBUG')
        self.flask_api_env = os.getenv('FLASK_ENV')
        self.flask_api_port = os.getenv('FLASK_PORT')
        self.date_timezone = os.getenv('TIMEZONE')
        self.api_key = os.getenv('API_KEY')

        self.jwt_blacklist_enabled = os.getenv('JWT_BLACKLIST_ENABLED')
        self.jwt_blacklist_token_check = os.getenv('JWT_BLACKLIST_TOKEN_CHECKS')
        self.jwt_error_message = os.getenv('JWT_ERROR_MESSAGE_KEY')
        self.jwt_access_token_expires = os.getenv('JWT_ACCESS_TOKEN_EXPIRES')
        self.jwt_propagate_exceptions = os.getenv('PROPAGATE_EXCEPTIONS')


class DbConstants(Constants):
    # Database tables names
    states_table = str()  # STATES
    town_table = str()    # TOWN
    city_table = str()    # CITY
    suburb_table = str()  # SUBURB

    def __init__(self):
        super().__init__()

        self.states_table = os.getenv('STATES').__str__()
        self.town_table = os.getenv('TOWN').__str__()
        self.city_table = os.getenv('CITY').__str__()
        self.suburb_table = os.getenv('SUBURB').__str__()

    class States:

        state_id = str()    # STATE_ID
        state_name = str()  # STATE_NAME
        state_key = str()   # STATE_KEY

        def __init__(self):

            self.state_id = os.getenv('STATE_ID').__str__()
            self.state_name = os.getenv('STATE_NAME').__str__()
            self.state_key = os.getenv('STATE_KEY').__str__()

    class Town:

        town_id = str()        # TOWN_ID
        town_name = str()      # TOWN_NAME
        town_key = str()       # TOWN_KEY
        town_state_id = str()  # TOWN_STATE_ID

        def __init__(self):

            self.town_id = os.getenv('TOWN_ID').__str__()
            self.town_name = os.getenv('TOWN_NAME').__str__()
            self.town_key = os.getenv('TOWN_KEY').__str__()
            self.town_state_id = os.getenv('TOWN_STATE_ID').__str__()

    class City:

        city_id = str()       # CITY_ID
        city_name = str()     # CITY_NAME
        city_key = str()      # CITY_KEY
        city_town_id = str()  # CITY_TOWN_ID

        def __init__(self):

            self.city_id = os.getenv('CITY_ID').__str__()
            self.city_name = os.getenv('CITY_NAME').__str__()
            self.city_key = os.getenv('CITY_KEY').__str__()
            self.city_town_id = os.getenv('CITY_TOWN_ID').__str__()

    class Suburb:

        suburb_id = str()           # SUBURB_ID
        suburb_name = str()         # SUBURB_NAME
        suburb_type = str()         # SUBURB_TYPE
        suburb_zone = str()         # SUBURB_ZONE
        suburb_postal_code = str()  # SUBURB_POSTAL_CODE
        suburb_city_id = str()      # SUBURB_CITY_ID

        def __init__(self):

            self.suburb_id = os.getenv('SUBURB_ID').__str__()
            self.suburb_name = os.getenv('SUBURB_NAME').__str__()
            self.suburb_type = os.getenv('SUBURB_TYPE').__str__()
            self.suburb_zone = os.getenv('SUBURB_ZONE').__str__()
            self.suburb_postal_code = os.getenv('SUBURB_POSTAL_CODE').__str__()
            self.suburb_city_id = os.getenv('SUBURB_CITY_ID').__str__()
