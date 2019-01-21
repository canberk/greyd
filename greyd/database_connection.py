# -*- coding: utf-8 -*-

"""
    File name: database_connection.py
    Author: Canberk Özdemir
    Date created: 2/5/2018
    Date last modified: 1/21/2019
    Python version: 3.5.2

    This module contains database constants.
"""

import os.path


class DatabeseGreyd(object):
    """greyd.db"""

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DATABASE = "greyd.db"

    def __init__(self):
        self.db_path = os.path.join(self.BASE_DIR, self.DATABASE)
