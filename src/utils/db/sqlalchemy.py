import alembic
from tqdm.auto import tqdm

import sqlalchemy as sa

from ..iterate import chunks
from ..logging import logger


def set_fast_sqlite_pragmas(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA synchronous=OFF")
    cursor.execute("PRAGMA journal_mode=OFF")
    cursor.execute("PRAGMA page_size=8192")
    cursor.execute("PRAGMA cache_size=5000")
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.execute("PRAGMA locking_mode=EXCLUSIVE")
    cursor.close()


def drop_sqlite_indexes(session):
    indexes = list(session.execute("SELECT * FROM sqlite_master WHERE type = 'index'"))
    for _, name, _, _, _ in indexes:
        if name.startswith("ix"):
            session.execute("DROP INDEX " + name)
    session.execute("VACUUM")
    session.commit()


def sa_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in sa.inspect(obj).mapper.column_attrs}


def auto_upgrade_engine(engine, meta):
    def flatten_operations(operations):
        def get_op(operation_object):
            if not hasattr(operation_object, "ops"):
                return operation_object
            return list(map(get_op, operation_object.ops))

        def flatten_list(flatten_this):
            if isinstance(flatten_this, list):
                return sum(map(flatten_list, flatten_this), [])
            return [flatten_this]

        return flatten_list(get_op(operations))

    connection = engine.connect()
    migration_context = alembic.migration.MigrationContext.configure(connection)
    op = alembic.operations.Operations(migration_context)
    migration_script = alembic.autogenerate.produce_migrations(migration_context, meta)
    for operation in flatten_operations(migration_script.upgrade_ops):
        logger.info(
            "auto_upgrade %s: %s",
            operation.to_diff_tuple()[0].upper(),
            operation.to_diff_tuple()[1],
        )
        op.invoke(operation)
    connection.close()


def copy_database(source_engine, target_engine, metadata: sa.schema.MetaData, chunk_size: int):

    if target_engine.dialect.name == "sqlite":
        sa.event.listen(target_engine, "connect", set_fast_sqlite_pragmas)

    Session_source = sa.orm.sessionmaker(bind=source_engine)
    Session_dest = sa.orm.sessionmaker(bind=target_engine, autocommit=False)
    metadata.create_all(bind=target_engine)
    sess_source = Session_source()

    # drop index definitions
    for table in metadata.sorted_tables:
        for index in table.indexes:
            index.drop(bind=target_engine)

    for table in metadata.sorted_tables:
        sess_dest = Session_dest()
        query = sess_source.query(table).yield_per(chunk_size)
        bar = tqdm(smoothing=0.1, desc=str(table), total=query.count())
        rows = (row._asdict() for row in query)
        for chunk in chunks(rows, chunksize=chunk_size):
            sess_dest.execute(table.insert(), chunk)
            bar.update(len(chunk))
        bar.close()
        sess_dest.commit()

    # recreate indexes
    auto_upgrade_engine(target_engine, metadata)
