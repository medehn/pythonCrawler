from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, drop_database

Base = declarative_base()


class LinkList(Base):
    __tablename__ = 'linklist'

    id = Column(Integer, primary_key=True)
    inputUrl = Column(String(250), nullable=False)
    links = Column(String(250))


engine = create_engine('sqlite:///linklist.db')
drop_database(engine.url)
Base.metadata.create_all(engine)
