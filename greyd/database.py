# -*- coding: utf-8 -*-

"""
    File name: database_connection.py
    Author: Canberk Özdemir
    Date created: 2/5/2018
    Date last modified: 1/22/2019
    Python version: 3.7.2

    This module contains database constants.
"""

import os.path
import config

class DatabaseGreyd(object):
    """Database connection"""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__)) + config.DB_PATH
    DATABASE = config.DB_NAME

    def __init__(self):
        self.db_path = os.path.join(self.BASE_DIR, self.DATABASE)
