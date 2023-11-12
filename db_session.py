from init_db import engine
from sqlalchemy.orm import sessionmaker

"""
This module is responsible for creating a SQLAlchemy Session using the engine from init_db.py.
By abstracting the session creation to this module, we ensure that all files 
that need to interact with the database use the same session configuration (eg. engine)
It also avoids duplicating the session creation code in multiple places. 

I used this abstraction because it allows me to control the scope of the session. 
We might want to use a new session for each request, or share a session across multiple
requests. Managing it here helps me easily implement the desired session scope.
"""

Session = sessionmaker(bind=engine)
session = Session()
