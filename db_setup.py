from sqlalchemy import create_engine
import sys
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class LinkList(Base):
   __tablename__ = 'linklist'

   id = Column(Integer, primary_key=True)
   inputUrl = Column(String(250), nullable=False)
   links = Column(String(250))

engine = create_engine('sqlite:///linklist.db')
Base.metadata.create_all(engine)

