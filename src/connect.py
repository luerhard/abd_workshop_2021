from configparser import ConfigParser
from typing import Tuple
from typing import Union

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.engine.base import Engine

import src


def get_config() -> ConfigParser:
    config = ConfigParser()
    config_path = src.PATH / "config.ini"
    config.read(config_path)
    return config


def create_wos_engine(echo: bool = False) -> Engine:
    """creates a sqlalchemy engine that is connected to the FIZ database"""
    config = get_config()

    user = config["fizDB"]["username"]
    password = config["fizDB"]["password"]

    host = "biblio-p-db01"
    port = 1521
    service_name = "bibliodb01.fiz.karlsruhe"

    schema = config["fizDB"]["schema"]

    return sa.create_engine(
        f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={service_name}",
        echo=echo,
        execution_options={"schema_translate_map": {None: schema}},
    )


def create_wos_session(
    echo: bool = False,
    sessionmaker: bool = False,
) -> Tuple[Engine, Union[orm.session.Session, orm.session.sessionmaker]]:
    """creates an enginer and a session for fizDB

    returns a tuple where the first element is always the engine and the second element is
    either a Session or a sessionmaker object
    """
    engine = create_wos_engine(echo=echo)
    Session = orm.sessionmaker(bind=engine)
    if sessionmaker:
        return engine, Session
    return engine, Session()


def fast_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA synchronous=OFF")
    cursor.execute("PRAGMA journal_mode=OFF")
    cursor.execute("PRAGMA page_size=8192")
    cursor.execute("PRAGMA cache_size=5000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA locking_mode=EXCLUSIVE")
    cursor.close()


def create_sqlite_engine(
    path,
    echo: bool = False,
    fast_pragmas: bool = True,
) -> Engine:
    engine = sa.create_engine(f"sqlite:///{path}", echo=echo)

    if fast_pragmas:
        sa.event.listen(engine, "connect", fast_sqlite_pragmas)

    return engine


def create_sqlite_session(
    path,
    echo: bool = False,
    sessionmaker: bool = False,
    fast_pragmas: bool = True,
) -> Tuple[Engine, Union[orm.session.Session, orm.session.sessionmaker]]:

    engine = create_sqlite_engine(path, echo, fast_pragmas)

    Session = orm.sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)

    if sessionmaker:
        return engine, Session
    return engine, Session()
