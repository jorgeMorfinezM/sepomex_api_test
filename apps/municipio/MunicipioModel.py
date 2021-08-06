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
from apps.estado.EstadoModel import EstadoModel
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

MUNICIPIO_ID_SEQ = Sequence('municipio_seq')  # define sequence explicitly


class MunicipioModel(Base):
    r"""
    Class to instance the data of MunicipioModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Select:
    """

    __tablename__ = cfg_db.town_table.__str__()

    id_municipio = Column(cfg_db.Town.town_id, Integer, MUNICIPIO_ID_SEQ,
                          primary_key=True, server_default=MUNICIPIO_ID_SEQ.next_value())
    nombre_municipio = Column(cfg_db.Town.town_name, String, nullable=False)
    clave_municipio = Column(cfg_db.Town.town_key, Integer, nullable=False, index=True)

    ciudad_id_estado = Column(
        cfg_db.Town.town_state_id,
        Integer,
        ForeignKey('EstadoModel.id_estado', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
        unique=True
        # no need to add index=True, all FKs have indexes
    )

    id_estado = relationship(EstadoModel,
                             backref=cfg_db.states_table.__str__())

    def __init__(self, data_town):
        self.nombre_municipio = data_town.get('nombre_municipio')
        self.clave_municipio = data_town.get('clave_municipio')
        self.ciudad_id_estado = data_town.get('id_estado')

    def check_if_row_exists(self, session, data):
        """
        Validate if row exists on database from dictionary data

        :param session: Session database object
        :param data: Dictionary with data to make validation function
        :return: row_exists: Object with boolean response from db
        """

        row_exists = None
        id_town = 0

        try:
            # for example to check if the insert on db is correct
            row_town = self.get_town_id(session, data)

            if row_town is not None:
                id_town = row_town.id_municipio
            else:
                id_town = 0

            logger.info('Municipio Row object in DB: %s', str(id_town))

            row_exists = session.query(MunicipioModel).filter(MunicipioModel.id_municipio == id_town).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_municipio'),
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

                new_row = MunicipioModel(data)

                logger.info('New Row Municipio: %s', str(new_row.nombre_municipio))

                session.add(new_row)

                row_town = self.get_town_id(session, data)

                logger.info('Municipio ID Inserted: %s', str(row_town.id_municipio))

                session.flush()

                data['id_municipio'] = row_town.id_municipio

                # check insert correct
                row_inserted = self.get_one_town(session, data)

                logger.info('Data Municipio inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:
                    endpoint_response = json.dumps({
                        "id_municipio": row_inserted.id_municipio,
                        "nombre_municipio": row_inserted.nombre_municipio,
                        "clave_municipio": row_inserted.clave_municipio,
                        "clave_estado": row_inserted.ciudad_id_estado
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_municipio'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    @staticmethod
    def get_town_id(session, data):
        """
        Get Municipio object row registered on database to get the ID

        :param session: Database session object
        :param data: Dictionary with data to get row
        :return: row_town: The row on database registered
        """

        row_town = None

        try:

            row_exists = session.query(MunicipioModel).\
                filter(MunicipioModel.nombre_municipio == data.get('nombre_municipio')).\
                filter(MunicipioModel.clave_municipio == data.get('clave_municipio')).scalar()

            logger.info('Row Data Municipio Exists on DB: %s', str(row_exists))

            if row_exists:

                row_town = session.query(MunicipioModel). \
                    filter(MunicipioModel.nombre_municipio == data.get('nombre_municipio')). \
                    filter(MunicipioModel.clave_municipio == data.get('clave_municipio')).one()

                logger.info('Row ID Municipio data from database object: {}'.format(str(row_town)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_municipio'), MunicipioModel.__tablename__, str(str(exc.args) + ':' +
                                                                                    str(exc.code))
                )
            )

        finally:
            session.close()

        return row_town

    @staticmethod
    def get_one_town(session, data):
        row = None

        try:

            row = session.query(MunicipioModel).\
                filter(MunicipioModel.nombre_municipio == data.get('nombre_municipio')).\
                filter(MunicipioModel.clave_municipio == data.get('clave_municipio')).one()

            if row:
                logger.info('Data Municipio on Db: %s',
                            'Nombre: {}, Clave: {}, Estado: {}'.format(row.nombre_municipio,
                                                                       row.clave_municipio,
                                                                       row.ciudad_id_estado))

        except SQLAlchemyError as exc:
            row = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_municipio'), MunicipioModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_towns(session, data):
        """
        Get all Municipios objects data registered on database.

        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param session: Database session
        :return: json.dumps dict
        """

        all_towns = None
        town_data = []

        page = None
        per_page = None

        all_towns = session.query(MunicipioModel).all()

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

            all_towns = session.query(MunicipioModel).paginate(page=page, per_page=per_page, error_out=False).all()

        for town in all_towns:
            town_id = town.estado_id
            town_name = town.nombre_municipio
            town_key = town.clave_municipio
            town_id_state = town.ciudad_id_estado

            town_data += [{
                "State": {
                    "id_municipio": str(town_id),
                    "nombre_municipio": town_name,
                    "clave_municipio": town_key,
                    "clave_estado": town_id_state
                }
            }]

        return json.dumps(town_data)

    @staticmethod
    def get_towns_by_filters(session, data, filter_spec):
        """
        Get list of Municipios filtered by options by user request

        :param session: Database session
        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param filter_spec: List of options defined by user request
        :return: json.dumps dict
        """

        page = 1
        per_page = 10

        query_result = None
        town_data = []

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

        query_result = session.query(MunicipioModel).all()

        query = session.query(MunicipioModel)

        filtered_query = apply_filters(query, filter_spec)

        if filter_spec is not None and filtered_query is not None:
            query_result = filtered_query.paginate(page=page, per_page=per_page, error_out=False).all()

        logger.info('Query filtered resultSet: %s', str(query_result))

        for town in query_result:
            town_id = town.estado_id
            town_name = town.nombre_municipio
            town_key = town.clave_municipio
            town_id_state = town.ciudad_id_estado

            town_data += [{
                "State": {
                    "id_municipio": str(town_id),
                    "nombre_municipio": town_name,
                    "clave_municipio": town_key,
                    "clave_estado": town_id_state
                }
            }]

        return json.dumps(town_data)

    def __repr__(self):
        return "<MunicipioModel(id_municipio='%s', " \
               "                nombre_municipio='%s', " \
               "                clave_municipio='%s', " \
               "                ciudad_id_estado='%s')>" % (self.id_municipio,
                                                            self.nombre_municipio,
                                                            self.clave_municipio,
                                                            self.ciudad_id_estado)
