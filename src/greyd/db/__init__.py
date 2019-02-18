# -*- coding: utf-8 -*-

"""Create or use sqlite database with sqlAlchemy"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from greyd.db.base import Base
from greyd import models
from greyd import config

# pylint: disable=invalid-name

engine = create_engine(
    "sqlite:///{}{}".format(config.DB_PATH, config.DB_NAME))

# Create tables
Base.metadata.create_all(engine)

Base.metadata.bind = engine
Session = sessionmaker(bind=engine)
session = Session()
