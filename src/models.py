# type: ignore
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import object_session
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey

Base = declarative_base()


class Str:
    def __repr__(self):
        name = self.__class__.__name__

        columns = self.__table__.c
        colnames = [f"{c.name}={getattr(self, c.name)}" for c in columns]

        return f"{name}({', '.join(colnames)})"


class ItemAuthorInstitution(Base, Str):
    __tablename__ = "items_authors_institutions"

    pk_itm_auth_inst = Column(Integer, primary_key=True)
    role = Column(String)

    fk_authors = Column(Integer, ForeignKey("authors.pk_authors"))
    fk_items = Column(Integer, ForeignKey("items.pk_items"))


class Abstract(Base, Str):
    __tablename__ = "abstracts"

    pk_abstracts = Column(Integer, primary_key=True)
    fk_items = Column(Integer, ForeignKey("items.pk_items"), index=True)
    text = Column(Text)


class Author(Base, Str):
    __tablename__ = "authors"

    pk_authors = Column(Integer, primary_key=True)
    fullname = Column(String)
    lastname = Column(String)
    firstname = Column(String)
    middlename = Column(String)
    author_group = Column(String)
    role = Column(String)
    orcid_id = Column(String)
    orcid_id_tr = Column(String)
    r_id = Column(String)
    r_id_tr = Column(String)

    items = relationship(
        "Item",
        secondary=ItemAuthorInstitution.__table__,
        back_populates="authors",
    )

    @property
    def coauthors(self):
        author_items = (
            object_session(self)
            .query(Author)
            .join(Author.items)
            .filter(Author.pk_authors == self.pk_authors)
            .with_entities(Item.pk_items)
            .distinct()
        )

        query = (
            object_session(self)
            .query(ItemAuthorInstitution)
            .join(Author)
            .filter(
                ItemAuthorInstitution.fk_items.in_(author_items),
                ItemAuthorInstitution.fk_authors != self.pk_authors,
            )
            .with_entities(Author)
            .distinct()
        )

        return query


class Item(Base, Str):
    __tablename__ = "items"

    pk_items = Column(Integer, primary_key=True)
    fk_sources = Column(Integer, ForeignKey("sources.pk_sources"))
    article_title = Column(String)
    doi = Column(String)
    page_cnt = Column(Integer)
    pubyear = Column(Integer, index=True)
    pubtype = Column(String)
    doctype = Column(String, index=True)
    d_author_cnt = Column(Integer)
    d_ref_cnt = Column(Integer)

    authors = relationship(
        "Author",
        secondary=ItemAuthorInstitution.__table__,
        back_populates="items",
    )

    source = relationship("Source", back_populates="items", uselist=False)


class Source(Base, Str):
    __tablename__ = "sources"

    pk_sources = Column(Integer, primary_key=True)
    sourcetitle = Column(String)
    canonical_sourcetitle = Column(String)
    pubtype = Column(String)
    issn = Column(String)

    items = relationship("Item", back_populates="source")
