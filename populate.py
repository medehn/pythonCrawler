from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import LinkList, Base

engine = create_engine('sqlite:///linklist.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)

session = DBSession()

