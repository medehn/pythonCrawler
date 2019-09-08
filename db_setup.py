from sqlalchemy import create_engine
from sqlalchemy import String
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# class for database setup - creating a database with two tables
Base = declarative_base()


class BaseUrl(Base):
    __tablename__ = 'bases'

    id = Column(Integer, primary_key=True)
    baseUrl = Column(String(250), nullable=False)
    links = relationship("RelatedLinks")


class RelatedLinks(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True)
    linkUrl = Column(String(250))
    linklist_id = Column(Integer, ForeignKey('bases.id'))


engine = create_engine('sqlite:///linklist.db')

Base.metadata.create_all(engine)
