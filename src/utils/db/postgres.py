import contextlib
from collections import Sequence
from typing import Iterable
from typing import Protocol
from typing import Union

from sqlalchemy.engine import Engine


class TableClass(Protocol):
    @property
    def __tablename__(self) -> str:
        ...


@contextlib.contextmanager
def disable_trigger(exec: Engine, table: Union[str, TableClass, Iterable[TableClass]]):
    def iter_names(item):
        if hasattr(item, "__tablename__"):
            yield item.__tablename__
        elif isinstance(item, str):
            yield item
        elif isinstance(item, Sequence):
            for i in item:
                yield from iter_names(i)

    for name in iter_names(table):
        exec.execute(f"ALTER TABLE {name} DISABLE TRIGGER ALL")
    yield
    for name in iter_names(table):
        exec.execute(f"ALTER TABLE {name} ENABLE TRIGGER ALL")
    return
