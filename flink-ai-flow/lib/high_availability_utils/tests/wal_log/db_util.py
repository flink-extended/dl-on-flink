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
import contextlib
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

SQL_ALCHEMY_DB_FILE = 'high_availability_utils.db'
SQL_ALCHEMY_CONN = "sqlite:///" + SQL_ALCHEMY_DB_FILE
engine = None
Session = None

"""
List of SQLAlchemy database engines for notification backend storage.
"""


def set_sql_alchemy_conn(db_conn: str):
    global SQL_ALCHEMY_CONN
    SQL_ALCHEMY_CONN = db_conn


def get_engine():
    global engine
    return engine


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
