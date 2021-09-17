#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
import contextlib
import re
import time
import urllib.parse
from collections import Iterable
from enum import Enum
from functools import wraps
from typing import Tuple, Union

from sqlalchemy import create_engine, Column, String, BigInteger, Text, Integer, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

from notification_service.base_notification import BaseEvent, Member, ANY_CONDITION
from notification_service.util.utils import event_model_to_event

if not hasattr(time, 'time_ns'):
    time.time_ns = lambda: int(time.time() * 1e9)

# use sqlite by default for testing
SQL_ALCHEMY_DB_FILE = 'notification_service.db'
SQL_ALCHEMY_CONN = "sqlite:///" + SQL_ALCHEMY_DB_FILE
engine = None
Session = None

"""
List of SQLAlchemy database engines for notification backend storage.
"""

MYSQL = 'mysql'
SQLITE = 'sqlite'
POSTGRES = 'postgresql'
MSSQL = 'mssql'
MONGODB = 'mongodb'

DATABASE_ENGINES = [
    MYSQL,
    SQLITE,
    POSTGRES,
    MSSQL,
    MONGODB,
]


class DBType(str, Enum):
    SQLITE = "sql_lite"
    MYSQL = "mysql"
    MONGODB = "mongodb"

    @staticmethod
    def value_of(db_type):
        if db_type in ('SQL_LITE', 'sql_lite', 'sqlite'):
            return DBType.SQLITE
        elif db_type in ('MYSQL', 'mysql'):
            return DBType.MYSQL
        elif db_type in ('MONGODB', 'mongodb'):
            return DBType.MONGODB
        else:
            raise NotImplementedError


def extract_db_engine_from_uri(db_uri):
    """
    Parse specified database URI to extract database type. Confirm extracted database engine is
    supported. If database driver is specified, confirm driver passes a plausible regex.
    """
    scheme = urllib.parse.urlparse(db_uri).scheme
    scheme_plus_count = scheme.count('+')

    """validates scheme parsed from DB URI is supported"""
    if scheme_plus_count == 0:
        db_engine = scheme
    elif scheme_plus_count == 1:
        db_engine, _ = scheme.split('+')
    else:
        error_msg = "Invalid database URI: '%s'." % db_uri
        raise Exception(error_msg)

    """validates db_engine parsed from DB URI is supported"""
    if db_engine not in DATABASE_ENGINES:
        error_msg = "Invalid database engine: '%s'." % db_engine
        raise Exception(error_msg)

    return db_engine


def parse_mongo_uri(db_uri):
    """
    Parse MongoDB URI-style string to split up and return credentials

    Args:
        db_uri (string): MongoDB URI-style string
    Return:

    """
    regex_str = r'^(?P<schema>(mongodb:(?:\/{2})?))((?P<user>\w+?):(?P<pwd>(\w+?))@|:@?)(?P<host>(\S+?)):(?P<port>(\d+))(\/(?P<db>(\S+?)))$'
    pattern = re.compile(regex_str)
    m = pattern.match(db_uri)
    if m is None:
        raise Exception('The URI of MongoDB is invalid')
    return m.group('user'), m.group('pwd'), m.group('host'), m.group('port'), m.group('db')


def prepare_db(user_engine=None, user_session=None, print_sql=False):
    global engine
    global Session
    if user_engine is not None and user_session is not None:
        engine = user_engine
        Session = user_session
    if engine is None or Session is None:
        engine_args = {'encoding': "utf-8"}
        if print_sql:
            engine_args['echo'] = True
        engine = create_engine(SQL_ALCHEMY_CONN, **engine_args)
        Session = scoped_session(
            sessionmaker(autocommit=False,
                         autoflush=False,
                         bind=engine,
                         expire_on_commit=False))


@contextlib.contextmanager
def create_session():
    prepare_db()
    session = Session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def provide_session(func):
    """
    Function decorator that provides a session if it isn't provided.
    If you want to reuse a session or run the function as part of a
    database transaction, you pass it to the function, if not this wrapper
    will create one and close it for you.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        arg_session = 'session'

        func_params = func.__code__.co_varnames
        session_in_args = arg_session in func_params and \
                          func_params.index(arg_session) < len(args)
        session_in_kwargs = arg_session in kwargs

        if session_in_kwargs or session_in_args:
            return func(*args, **kwargs)
        else:
            with create_session() as session:
                kwargs[arg_session] = session
                return func(*args, **kwargs)

    return wrapper


Base = declarative_base()


class EventModel(Base):
    __tablename__ = "event_model"
    version = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    key = Column(String(1024), nullable=False)
    value = Column(Text())
    event_type = Column(String(1024), server_default="UNDEFINED")
    context = Column(Text())
    namespace = Column(String(1024))
    sender = Column(String(1024))
    create_time = Column(BigInteger(), nullable=False)
    uuid = Column(String(40), nullable=False, unique=True)

    @staticmethod
    @provide_session
    def add_event(event: BaseEvent, uuid, session=None):
        event_model = EventModel()
        event_model.key = event.key
        event_model.value = event.value
        event_model.event_type = event.event_type
        event_model.context = event.context
        event_model.namespace = event.namespace
        event_model.create_time = int(time.time() * 1000)
        event_model.uuid = uuid
        event_model.sender = event.sender
        session.add(event_model)
        session.commit()
        return event_model_to_event(event_model)

    @staticmethod
    @provide_session
    def list_events(key: Union[str, Tuple[str]],
                    version: int = None,
                    event_type: str = None,
                    start_time: int = None,
                    namespace: str = None,
                    sender: str = None,
                    session=None):
        key = None if key == "" else key
        event_type = None if event_type == "" else event_type
        namespace = None if namespace == "" else namespace
        sender = None if sender == "" else sender
        if isinstance(key, str):
            key = (key,)
        elif isinstance(key, Iterable):
            key = tuple(key)
        if key is None:
            raise Exception('key cannot be empty.')

        conditions = []
        if event_type is not None and event_type != ANY_CONDITION:
            conditions.append(EventModel.event_type == event_type)
        if start_time is not None and start_time > 0:
            conditions.append(EventModel.create_time >= start_time)
        if namespace is not None and ANY_CONDITION != namespace:
            conditions.append(EventModel.namespace == namespace)
        if sender is not None and ANY_CONDITION != sender:
            conditions.append(EventModel.sender == sender)
        if version > 0:
            conditions.append(EventModel.version > version)
        if ANY_CONDITION not in key:
            conditions.append(EventModel.key.in_(key))
        event_model_list = session.query(EventModel).filter(*conditions).all()
        return [event_model_to_event(event_model) for event_model in event_model_list]

    @staticmethod
    @provide_session
    def list_all_events(start_time: int, session=None):
        conditions = [
            EventModel.create_time >= start_time
        ]
        event_model_list = session.query(EventModel).filter(*conditions).all()
        return [event_model_to_event(event_model) for event_model in event_model_list]

    @staticmethod
    @provide_session
    def list_all_events_from_version(start_version: int, end_version: int = None, session=None):
        conditions = [
            EventModel.version > start_version
        ]
        if end_version is not None and end_version > 0:
            conditions.append(EventModel.version <= end_version)
        event_model_list = session.query(EventModel).filter(*conditions).all()
        return [event_model_to_event(event_model) for event_model in event_model_list]

    @staticmethod
    @provide_session
    def sync_event(event: BaseEvent, uuid, session=None):
        event_model = EventModel()
        event_model.key = event.key
        event_model.value = event.value
        event_model.event_type = event.event_type
        event_model.context = event.context
        event_model.namespace = event.namespace
        event_model.create_time = event.create_time
        event_model.uuid = uuid
        event_model.sender = event.sender
        session.add(event_model)
        session.commit()
        return event_model_to_event(event_model)

    @staticmethod
    @provide_session
    def get_latest_version(session=None):
        return session.query(EventModel).order_by(EventModel.version.desc()) \
            .limit(1).first().version

    @staticmethod
    @provide_session
    def get_event_by_uuid(uuid, session=None):
        conditions = [
            EventModel.uuid == uuid
        ]
        return session.query(EventModel).filter(*conditions).first()

    @staticmethod
    def create_table(db_conn=None):
        if db_conn is not None:
            global SQL_ALCHEMY_CONN
            SQL_ALCHEMY_CONN = db_conn
        prepare_db()
        if not engine.dialect.has_table(engine, EventModel.__tablename__):
            Base.metadata.create_all(engine)

    @staticmethod
    @provide_session
    def cleanup(session=None):
        session.query(EventModel).delete()
        session.commit()


class ClientModel(Base):
    __tablename__ = "notification_client"
    id = Column(BigInteger().with_variant(Integer, "sqlite"), autoincrement=True, primary_key=True)
    namespace = Column(String(1024))
    sender = Column(String(1024))
    create_time = Column(BigInteger)

    @staticmethod
    @provide_session
    def register_client(namespace: str = None, sender: str = None, session=None):
        client = ClientModel()
        client.namespace = namespace
        client.sender = sender
        client.create_time = int(time.time() * 1000)
        session.add(client)
        session.commit()
        return client.id

    @staticmethod
    @provide_session
    def delete_client(client_id, session=None):
        client_to_delete = session.query(ClientModel).filter(ClientModel.id == client_id).first()
        if client_to_delete is None:
            raise Exception("You are trying to delete an non-existing notification client!")
        session.delete(client_to_delete)
        session.commit()

    @staticmethod
    @provide_session
    def is_client_exists(client_id, session=None):
        client_to_check = session.query(ClientModel).filter(ClientModel.id == client_id).first()
        return client_to_check is not None

    @staticmethod
    def create_table(db_conn=None):
        if db_conn is not None:
            global SQL_ALCHEMY_CONN
            SQL_ALCHEMY_CONN = db_conn
        prepare_db()
        if not engine.dialect.has_table(engine, ClientModel.__tablename__):
            Base.metadata.create_all(engine)


class MemberModel(Base):
    __tablename__ = "member_model"
    id = Column(BigInteger().with_variant(Integer, "sqlite"), primary_key=True)
    version = Column(BigInteger(), nullable=False)
    server_uri = Column(String(767), nullable=False, unique=True)
    update_time = Column(BigInteger(), nullable=False)
    uuid = Column(String(128), nullable=False, unique=True)

    @staticmethod
    def create_table(db_conn=None):
        if db_conn is not None:
            global SQL_ALCHEMY_CONN
            SQL_ALCHEMY_CONN = db_conn
        prepare_db()
        if not engine.dialect.has_table(engine, MemberModel.__tablename__):
            Base.metadata.create_all(engine)

    @staticmethod
    @provide_session
    def cleanup(session=None):
        session.query(MemberModel).delete()
        session.commit()

    @staticmethod
    @provide_session
    def update_member(server_uri, server_uuid, session=None):
        member = session.query(MemberModel) \
            .filter(MemberModel.server_uri == server_uri).first()
        if member is None:
            member = MemberModel()
            member.version = 1
            member.server_uri = server_uri
            member.update_time = time.time_ns() / 1000000
            member.uuid = server_uuid
            session.add(member)
        else:
            if member.uuid != server_uuid:
                raise Exception("The server uri '%s' is already exists in the storage!" %
                                server_uri)
            member.version += 1
            member.update_time = time.time_ns() / 1000000
        session.commit()

    @staticmethod
    @provide_session
    def get_living_members(ttl, session=None):
        member_models = session.query(MemberModel) \
            .filter(MemberModel.update_time >= time.time_ns() / 1000000 - ttl) \
            .all()
        return [Member(m.version, m.server_uri, int(m.update_time)) for m in member_models]

    @staticmethod
    @provide_session
    def get_dead_members(ttl, session=None):
        member_models = session.query(MemberModel) \
            .filter(MemberModel.update_time < time.time_ns() / 1000000 - ttl) \
            .all()
        return [Member(m.version, m.server_uri, int(m.update_time)) for m in member_models]

    @staticmethod
    @provide_session
    def delete_member(server_uri=None, server_uuid=None, session=None):
        conditions = []
        if server_uri:
            conditions.append(MemberModel.server_uri == server_uri)
        if server_uuid:
            conditions.append(MemberModel.uuid == server_uuid)
        if len(conditions) != 1:
            raise Exception("Please provide exactly one param, server_uri or server_uuid")
        member = session.query(MemberModel).filter(*conditions).first()
        if member is not None:
            session.delete(member)
        session.commit()

    @staticmethod
    @provide_session
    def clear_dead_members(ttl, session=None):
        session.query(MemberModel) \
            .filter(MemberModel.update_time < time.time_ns() / 1000000 - ttl) \
            .delete()
        session.commit()
