from configparser import ConfigParser

import sqlalchemy as sa
from sqlalchemy import create_engine
from sqlalchemy import orm

import src


def get_config() -> ConfigParser:
    config = ConfigParser()
    config_path = src.PATH / "config.ini"
    config.read(config_path)
    return config


def create_wos_engine(echo: bool = False) -> sa.engine.base.Engine:
    """creates a sqlalchemy engine that is connected to the FIZ database"""
    config = get_config()

    user = config["fizDB"]["username"]
    password = config["fizDB"]["password"]

    host = "biblio-p-db01"
    port = 1521
    service_name = "bibliodb01.fiz.karlsruhe"

    schema = config["fizDB"]["schema"]

    return create_engine(
        f"oracle+cx_oracle://{user}:{password}@{host}:{port}/?service_name={service_name}",
        echo=echo,
        execution_options={"schema_translate_map": {"per_user": schema}},
    )


def create_wos_session(echo=False, sessionmaker=False):
    engine = create_wos_engine(echo=echo)
    Session = orm.sessionmaker(bind=engine)
    if sessionmaker:
        return engine, Session
    return engine, Session()


def create_sqlite_session(path, echo=False, sessionmaker=False, fast_pragmas=True):
    engine = sa.create_engine(
        f"sqlite:///{path}",
        execution_options={"schema_translate_map": {"per_user": None}},
        echo=echo,
    )
    Session = orm.sessionmaker(bind=engine, expire_on_commit=False, autocommit=False)

    if sessionmaker:
        return engine, Session
    return engine, Session()
