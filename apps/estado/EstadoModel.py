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
from sqlalchemy_filters import apply_filters
from sqlalchemy import Column, Numeric, Integer, String, Date, Time, Sequence
from db_controller.database_backend import *
from db_controller import mvc_exceptions as mvc_exc

cfg_db = get_config_settings_db()

ESTADO_ID_SEQ = Sequence('estado_seq')  # define sequence explicitly


class EstadoModel(Base):
    r"""
    Class to instance the data of EstadoModel on the database.
    Transactions:
     - Insert: Add data to the database if not exists.
     - Select:
    """

    __tablename__ = cfg_db.states_table.__str__()

    id_estado = Column(cfg_db.States.state_id, Integer, ESTADO_ID_SEQ,
                       primary_key=True, server_default=ESTADO_ID_SEQ.next_value())
    nombre_estado = Column(cfg_db.States.state_name, String, nullable=False, index=True)
    clave_estado = Column(cfg_db.States.state_key, Integer, nullable=False, index=True)

    def __init__(self, data_driver):
        self.nombre_estado = data_driver.get('nombre_estado')
        self.clave_estado = data_driver.get('clave_estado')

    def check_if_row_exists(self, session, data):
        """
        Validate if row exists on database from dictionary data

        :param session: Session database object
        :param data: Dictionary with data to make validation function
        :return: row_exists: Object with boolean response from db
        """

        row_exists = None
        id_estado = 0

        try:
            # for example to check if the insert on db is correct
            row_estado = self.get_state_id(session, data)

            if row_estado is not None:
                id_estado = row_estado.id_estado
            else:
                id_estado = 0

            logger.info('Estado Row object in DB: %s', str(id_estado))

            row_exists = session.query(EstadoModel).filter(EstadoModel.id_estado == id_estado).scalar()

            logger.info('Row to data: {}, Exists: %s'.format(data), str(row_exists))

        except SQLAlchemyError as exc:
            row_exists = None

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.IntegrityError(
                'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_estado'),
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

                new_row = EstadoModel(data)

                logger.info('New Row Estado: %s', str(new_row.nombre_estado))

                session.add(new_row)

                row_estado = self.get_state_id(session, data)

                logger.info('Estado ID Inserted: %s', str(row_estado.id_estado))

                session.flush()

                data['id_estado'] = row_estado.id_estado

                # check insert correct
                row_inserted = self.get_one_state(session, data)

                logger.info('Data Estado inserted: %s, Original Data: {}'.format(data), str(row_inserted))

                if row_inserted:

                    endpoint_response = json.dumps({
                        "id_estado": row_inserted.id_estado,
                        "nombre_estado": row_inserted.nombre_estado,
                        "clave_estado": row_inserted.clave_estado
                    })

            except SQLAlchemyError as exc:
                endpoint_response = None
                session.rollback()

                logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                                 str(exc.code)))
                raise mvc_exc.IntegrityError(
                    'Row not stored in "{}". IntegrityError: {}'.format(data.get('nombre_estado'),
                                                                        str(str(exc.args) + ':' + str(exc.code)))
                )
            finally:
                session.close()

        return endpoint_response

    @staticmethod
    def get_state_id(session, data):
        """
        Get Estado object row registered on database to get the ID

        :param session: Database session object
        :param data: Dictionary with data to get row
        :return: row_estado: The row on database registered
        """

        row_estado = None

        try:

            row_exists = session.query(EstadoModel).filter(EstadoModel.nombre_estado == data.get('nombre_estado')).\
                filter(EstadoModel.clave_estado == data.get('clave_estado')).scalar()

            logger.info('Row Data Estado Exists on DB: %s', str(row_exists))

            if row_exists:

                row_estado = session.query(EstadoModel). \
                    filter(EstadoModel.nombre_estado == data.get('nombre_estado')). \
                    filter(EstadoModel.clave_estado == data.get('clave_estado')).one()

                logger.info('Row ID Estado data from database object: {}'.format(str(row_estado)))

        except SQLAlchemyError as exc:

            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))
            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_estado'), EstadoModel.__tablename__, str(str(exc.args) + ':' +
                                                                              str(exc.code))
                )
            )

        finally:
            session.close()

        return row_estado

    @staticmethod
    def get_one_state(session, data):
        row = None

        try:

            row = session.query(EstadoModel).filter(EstadoModel.id_estado == data.get('id_estado')).\
                filter(EstadoModel.clave_estado == data.get('clave_estado')).one()

            if row:
                logger.info('Data Estado on Db: %s',
                            'Nombre Estado: {}, Clave Estado: {}'.format(row.nombre_estado,
                                                                         row.clave_estado))

        except SQLAlchemyError as exc:
            row = None
            logger.exception('An exception was occurred while execute transactions: %s', str(str(exc.args) + ':' +
                                                                                             str(exc.code)))

            raise mvc_exc.ItemNotStored(
                'Can\'t read data: "{}" because it\'s not stored in "{}". Row empty: {}'.format(
                    data.get('nombre_estado'), EstadoModel.__tablename__, str(str(exc.args) + ':' + str(exc.code))
                )
            )

        finally:
            session.close()

        return row

    @staticmethod
    def get_all_states(session, data):
        """
        Get all States objects data registered on database.

        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param session: Database session
        :return: json.dumps dict
        """

        all_states = None
        states_data = []

        page = None
        per_page = None

        all_states = session.query(EstadoModel).all()

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

            all_states = session.query(EstadoModel).paginate(page=page, per_page=per_page, error_out=False).all()

        for state in all_states:
            state_id = state.id_estado
            state_name = state.nombre_estado
            state_key = state.clave_estado

            states_data += [{
                "State": {
                    "id_estado": str(state_id),
                    "nombre_estado": state_name,
                    "clave_estado": state_key
                }
            }]

        return json.dumps(states_data)

    @staticmethod
    def get_states_by_filters(session, data, filter_spec):
        """
        Get list of States filtered by options by user request

        :param session: Database session
        :param data: Dictionary contains relevant data to filter Query on resultSet DB
        :param filter_spec: List of options defined by user request
        :return: json.dumps dict
        """

        page = 1
        per_page = 10

        query_result = None
        states_data = []

        if 'offset' in data.keys() and 'limit' in data.keys():
            page = data.get('offset')
            per_page = data('limit')

        query_result = session.query(EstadoModel).all()

        query = session.query(EstadoModel)

        filtered_query = apply_filters(query, filter_spec)

        if filter_spec is not None and filtered_query is not None:
            query_result = filtered_query.paginate(page=page, per_page=per_page, error_out=False).all()

        logger.info('Query filtered resultSet: %s', str(query_result))

        for state in query_result:
            state_id = state.id_estado
            state_name = state.nombre_estado
            state_key = state.clave_estado

            states_data += [{
                "State": {
                    "id_estado": str(state_id),
                    "nombre_estado": state_name,
                    "clave_estado": state_key
                }
            }]

        return json.dumps(states_data)

    def __repr__(self):
        return "<EstadoModel(id_estado='%s', " \
               "             nombre_estado='%s', " \
               "             clave_estado='%s')>" % (self.id_estado, self.nombre_estado, self.clave_estado)
