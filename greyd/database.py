# -*- coding: utf-8 -*-

"""Database configure variables."""

import os.path
import config


class DatabaseGreyd(object):
    """Database connection"""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + config.DB_PATH
    DATABASE = config.DB_NAME

    def __init__(self):
        self.db_path = os.path.join(self.BASE_DIR, self.DATABASE)
