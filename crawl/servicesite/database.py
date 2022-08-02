from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from servicesite import settings

Base = declarative_base()


def db_connect() -> Engine:
    return create_engine(URL(**settings.DATABASE))

def create_table(engine: Engine):
    Base.metadata.create_all(engine)

class Pages(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True)
    site_id = Column('site_url', Integer)
    title = Column('title', String)
    description = Column('description', Integer)
    metadata = Column('metadata', String)

class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    name = Column('name', String(30), unique=True)
