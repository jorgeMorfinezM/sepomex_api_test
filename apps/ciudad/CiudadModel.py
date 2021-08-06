# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later


PostgreSQL DB backend.

Each one of the CRUD operations should be able to open a database connection if
there isn't already one available (check if there are any issues with this).

Documentation:
    About the Vehicle data on the database to generate CRUD operations from endpoint of the API:
    - Insert data
    - Update data
    - Delete data
    - Search data

"""

__author__ = "Jorge Morfinez Mojica (jorge.morfinez.m@gmail.com)"
__copyright__ = "Copyright 2021"
__license__ = ""
__history__ = """ """
__version__ = "1.21.H05.1 ($Rev: 2 $)"

import json
import logging
from apps.municipio.MunicipioModel import MunicipioModel
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

CITY_ID_SEQ = Sequence('city_seq')  # define sequence explicitly


class CiudadModel(Base):
    r"""
    Class to instance the data of CiudadModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = cfg_db.city_table.__str__()

    id_ciudad = Column(cfg_db.City.city_id, Integer, CITY_ID_SEQ,
                       primary_key=True, server_default=CITY_ID_SEQ.next_value())
    nombre_ciudad = Column(cfg_db.City.city_name, String, nullable=False, index=True)
    clave_ciudad = Column(cfg_db.City.city_key, Integer, nullable=False, index=True)

    ciudad_id_municipio = Column(
        cfg_db.City.city_town_id,
        Integer,
        ForeignKey('MunicipioModel.id_municipio', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
        unique=True
        # no need to add index=True, all FKs have indexes
    )

    id_municipio = relationship(MunicipioModel,
                                backref=cfg_db.town_table.__str__())

    def __init__(self, data_city):
        self.nombre_ciudad = data_city.get('nombre_ciudad')
        self.clave_ciudad = data_city.get('clave_ciudad')
        self.ciudad_id_municipio = data_city.get('id_municipio')

    def check_if_row_exists(self, session, data):
        """
        Validate if row exists on database from dictionary data

        :param session: Session database object
        :param data: Dictionary with data to make validation function
        :return: row_exists: Object with boolean response from db
        """

        row_exists = None
        id_city = 0

        try:
            # for example to check if the insert on db is correct
            row_city = self.get_city_id(session, data)

            if row_city is not None:
                id_city = row_city.id_ciudad
            else:
                id_city = 0

            logger.info('Municipio Row object in DB: %s', str(id_city))

            row_exists = session.query(CiudadModel).filter(CiudadModel.id_ciudad == id_city).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_ciudad'),
                                                                    str(str(exc.args) + ':' + str(exc.code)))
            )
        finally:
            session.close()

        return row_exists

    def insert_data(self, session, data):
        """
        Function to insert new row on database

        :param session: Session database object
        :param data: Dictionary to insert new the data containing on the db
        :return: endpoint_response
        """

        endpoint_response = None

        if not self.check_if_row_exists(session, data):

            try:

                new_row = CiudadModel(data)

                logger.info('New Row Ciudad: %s', str(new_row.nombre_ciudad))

                session.add(new_row)

                row_city = self.get_city_id(session, data)

                logger.info('Ciudad ID Inserted: %s', str(row_city.id_ciudad))

                session.flush()

                data['id_ciudad'] = row_city.id_ciudad

                # check insert correct
                row_inserted = self.get_one_city(session, data)

                logger.info('Data Ciudad inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:
                    endpoint_response = json.dumps({
                        "id_ciudad": str(row_inserted.id_ciudad),
                        "nombre_ciudad": row_inserted.nombre_ciudad,
                        "clave_ciudad": row_inserted.clave_ciudad,
                        "clave_municipio": row_inserted.ciudad_id_municipio
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_ciudad'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    @staticmethod
    def get_city_id(session, data):
        """
        Get Ciudad object row registered on database to get the ID

        :param session: Database session object
        :param data: Dictionary with data to get row
        :return: row_city: The row on database registered
        """

        row_city = None

        try:

            row_exists = session.query(CiudadModel). \
                filter(CiudadModel.nombre_ciudad == data.get('nombre_ciudad')). \
                filter(CiudadModel.clave_ciudad == data.get('clave_ciudad')).scalar()

            logger.info('Row Data Ciudad Exists on DB: %s', str(row_exists))

            if row_exists:
                row_city = session.query(CiudadModel). \
                    filter(CiudadModel.nombre_ciudad == data.get('nombre_ciudad')). \
                    filter(CiudadModel.clave_ciudad == data.get('clave_ciudad')).one()

                logger.info('Row ID Ciudad data from database object: {}'.format(str(row_city)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_ciudad'), CiudadModel.__tablename__, str(str(exc.args) + ':' +
                                                                              str(exc.code))
                )
            )

        finally:
            session.close()

        return row_city

    @staticmethod
    def get_one_city(session, data):
        row = None

        try:

            row = session.query(CiudadModel). \
                filter(CiudadModel.nombre_ciudad == data.get('nombre_ciudad')). \
                filter(CiudadModel.clave_ciudad == data.get('clave_ciudad')).one()

            if row:
                logger.info('Data Ciudad on Db: %s',
                            'Nombre: {}, Clave: {}, Estado: {}'.format(row.nombre_ciudad,
                                                                       row.clave_ciudad,
                                                                       row.ciudad_id_municipio))

        except SQLAlchemyError as exc:
            row = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_ciudad'), CiudadModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_cities(session, data):
        """
        Get all Ciudades objects data registered on database.

        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param session: Database session
        :return: json.dumps dict
        """

        all_cities = None
        city_data = []

        page = None
        per_page = None

        all_cities = session.query(CiudadModel).all()

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

            all_cities = session.query(CiudadModel).paginate(page=page, per_page=per_page, error_out=False).all()

        for city in all_cities:
            city_id = city.id_ciudad
            city_name = city.nombre_ciudad
            city_key = city.clave_ciudad
            city_id_town = city.ciudad_id_municipio

            city_data += [{
                "State": {
                    "id_ciudad": str(city_id),
                    "nombre_ciudad": city_name,
                    "clave_ciudad": city_key,
                    "clave_municipio": city_id_town
                }
            }]

        return json.dumps(city_data)

    @staticmethod
    def get_cities_by_filters(session, data, filter_spec):
        """
        Get list of Ciudades filtered by options by user request

        :param session: Database session
        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param filter_spec: List of options defined by user request
        :return: json.dumps dict
        """

        page = 1
        per_page = 10

        query_result = None
        city_data = []

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

        query_result = session.query(CiudadModel).all()

        query = session.query(CiudadModel)

        filtered_query = apply_filters(query, filter_spec)

        if filter_spec is not None and filtered_query is not None:
            query_result = filtered_query.paginate(page=page, per_page=per_page, error_out=False).all()

        logger.info('Query filtered resultSet: %s', str(query_result))

        for city in query_result:
            city_id = city.id_ciudad
            city_name = city.nombre_ciudad
            city_key = city.clave_ciudad
            city_id_town = city.ciudad_id_municipio

            city_data += [{
                "State": {
                    "id_ciudad": str(city_id),
                    "nombre_ciudad": city_name,
                    "clave_ciudad": city_key,
                    "clave_municipio": city_id_town
                }
            }]

        return json.dumps(city_data)

    def __repr__(self):
        return "<CiudadModel(id_ciudad='%s', " \
               "             nombre_ciudad='%s', " \
               "             clave_ciudad='%s', " \
               "             ciudad_id_municipio='%s')>" % (self.id_ciudad,
                                                            self.nombre_ciudad,
                                                            self.clave_ciudad,
                                                            self.ciudad_id_municipio)
