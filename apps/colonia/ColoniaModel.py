# -*- coding: utf-8 -*-

"""
Requires Python 3.8 or later


PostgreSQL DB backend.

Each one of the CRUD operations should be able to open a database connection if
there isn't already one available (check if there are any issues with this).

Documentation:
    About the Bank Bot data on the database to generate CRUD operations from endpoint of the API:
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
from apps.ciudad.CiudadModel import CiudadModel
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence, Float
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

SUBURB_ID_SEQ = Sequence('suburb_seq')  # define sequence explicitly


class ColoniaModel(Base):
    r"""
    Class to instance the data of ColoniaModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Update: Update data on the database if exists.
     - Delete:
     - Select:
    """

    __tablename__ = 'colonia'

    id_colonia = Column('id_colonia', Integer, SUBURB_ID_SEQ,
                        primary_key=True, server_default=SUBURB_ID_SEQ.next_value())
    nombre_colonia = Column('nombre_colonia', String, nullable=False, index=True)

    tipo_colonia = Column('tipo_asentamiento', String, nullable=False)

    zona_colonia = Column('zona_asentamiento', String, nullable=False)

    codigo_postal = Column('codigo_postal', String, nullable=False, index=True)

    colonia_id_ciudad = Column(
        'id_ciudad',
        Integer,
        ForeignKey('CiudadModel.id_ciudad', onupdate='CASCADE', ondelete='CASCADE'),
        nullable=True,
        unique=True
        # no need to add index=True, all FKs have indexes
    )

    id_ciudad = relationship(CiudadModel,
                             backref=cfg_db.city_table.__str__())

    def __init__(self, data_colonia):
        self.nombre_colonia = data_colonia.get('nombre_colonia')
        self.tipo_colonia = data_colonia.get('tipo_colonia')
        self.zona_colonia = data_colonia.get('zona')
        self.codigo_postal = data_colonia.get('codigo_postal')
        self.colonia_id_ciudad = data_colonia.get('id_ciudad')

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
            row_city = self.get_suburb_id(session, data)

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

                new_row = ColoniaModel(data)

                logger.info('New Row Colonia: %s', str(new_row.nombre_colonia))

                session.add(new_row)

                row_suburb = self.get_suburb_id(session, data)

                logger.info('Ciudad ID Inserted: %s', str(row_suburb.id_colonia))

                session.flush()

                data['id_colonia'] = row_suburb.id_colonia

                # check insert correct
                row_inserted = self.get_one_suburb(session, data)

                logger.info('Data Colonia inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:
                    endpoint_response = json.dumps({
                        "id_colonia": str(row_inserted.id_colonia),
                    "nombre_colonia": row_inserted.nombre_colonia,
                    "tipo_colonia": row_inserted.tipo_colonia,
                    "zona_colonia": row_inserted.zona_colonia,
                    "codigo_postal": row_inserted.codigo_postal,
                    "id_ciudad": str(row_inserted.colonia_id_ciudad)
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_colonia'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    @staticmethod
    def get_suburb_id(session, data):
        """
        Get Colonia object row registered on database to get the ID

        :param session: Database session object
        :param data: Dictionary with data to get row
        :return: row_suburb: The row on database registered
        """

        row_suburb = None

        try:

            row_exists = session.query(ColoniaModel). \
                filter(ColoniaModel.nombre_colonia == data.get('nombre_colonia')). \
                filter(ColoniaModel.tipo_colonia == data.get('tipo_colonia')). \
                filter(ColoniaModel.codigo_postal == data.get('codigo_postal')).scalar()

            logger.info('Row Data Colonia Exists on DB: %s', str(row_exists))

            if row_exists:
                row_suburb = session.query(ColoniaModel). \
                    filter(ColoniaModel.nombre_colonia == data.get('nombre_colonia')). \
                    filter(ColoniaModel.tipo_colonia == data.get('tipo_colonia')). \
                    filter(ColoniaModel.codigo_postal == data.get('codigo_postal')).one()

                logger.info('Row ID Colonia data from database object: {}'.format(str(row_suburb)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_colonia'), ColoniaModel.__tablename__, str(str(exc.args) + ':' +
                                                                                str(exc.code))
                )
            )

        finally:
            session.close()

        return row_suburb

    @staticmethod
    def get_one_suburb(session, data):
        row = None

        try:

            row = session.query(ColoniaModel). \
                    filter(ColoniaModel.nombre_colonia == data.get('nombre_colonia')). \
                    filter(ColoniaModel.tipo_colonia == data.get('tipo_colonia')). \
                    filter(ColoniaModel.zona_colonia == data.get('zona')). \
                    filter(ColoniaModel.codigo_postal == data.get('codigo_postal')).one()

            if row:
                logger.info('Data Colonia on Db: %s',
                            'Nombre: {}, Tipo: {}, Codigo Postal: {}'.format(row.nombre_colonia,
                                                                             row.tipo_colonia,
                                                                             row.codigo_postal))

        except SQLAlchemyError as exc:
            row = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_colonia'), ColoniaModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_suburbs(session, data):
        """
        Get all Colonias objects data registered on database.

        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param session: Database session
        :return: json.dumps dict
        """

        all_suburbs = None
        suburb_data = []

        page = None
        per_page = None

        all_suburbs = session.query(ColoniaModel).all()

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

            all_suburbs = session.query(ColoniaModel).paginate(page=page, per_page=per_page, error_out=False).all()

        for suburb in all_suburbs:
            suburb_id = suburb.id_colonia
            suburb_name = suburb.nombre_colonia
            suburb_type = suburb.tipo_colonia
            suburn_zone = suburb.zona_colonia
            zip_postal_code = suburb.codigo_postal
            city_id = suburb.colonia_id_ciudad

            suburb_data += [{
                "Suburb": {
                    "id_colonia": str(suburb_id),
                    "nombre_colonia": suburb_name,
                    "tipo_colonia": suburb_type,
                    "zona_colonia": suburn_zone,
                    "codigo_postal": zip_postal_code,
                    "id_ciudad": str(city_id)
                }
            }]

        return json.dumps(suburb_data)

    @staticmethod
    def get_suburbs_by_filters(session, data, filter_spec):
        """
        Get list of Colonias filtered by options by user request

        :param session: Database session
        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param filter_spec: List of options defined by user request
        :return: json.dumps dict
        """

        page = 1
        per_page = 10

        query_result = None
        suburb_data = []

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

        query_result = session.query(CiudadModel).all()

        query = session.query(CiudadModel)

        filtered_query = apply_filters(query, filter_spec)

        if filter_spec is not None and filtered_query is not None:
            query_result = filtered_query.paginate(page=page, per_page=per_page, error_out=False).all()

        logger.info('Query filtered resultSet: %s', str(query_result))

        for suburb in query_result:
            suburb_id = suburb.id_colonia
            suburb_name = suburb.nombre_colonia
            suburb_type = suburb.tipo_colonia
            suburn_zone = suburb.zona_colonia
            zip_postal_code = suburb.codigo_postal
            city_id = suburb.colonia_id_ciudad

            suburb_data += [{
                "Suburb": {
                    "id_colonia": str(suburb_id),
                    "nombre_colonia": suburb_name,
                    "tipo_colonia": suburb_type,
                    "zona_colonia": suburn_zone,
                    "codigo_postal": zip_postal_code,
                    "id_ciudad": str(city_id)
                }
            }]

        return json.dumps(suburb_data)

    def __repr__(self):
        return "<ColoniaModel(id_colonia='%s', " \
               "              nombre_colonia='%s', " \
               "              tipo_colonia='%s', " \
               "              zona_colonia='%s', " \
               "              codigo_postal='%s', " \
               "              colonia_id_ciudad='%s')>" % (self.id_colonia,
                                                           self.nombre_colonia,
                                                           self.tipo_colonia,
                                                           self.zona_colonia,
                                                           self.codigo_postal,
                                                           self.colonia_id_ciudad)
