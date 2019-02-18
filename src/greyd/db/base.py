# -*- coding: utf-8 -*-

"""SqlAlchemy Base object.
Models should be import this module.
Model class use Base object for parent class.
"""

from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()
