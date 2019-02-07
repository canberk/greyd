# -*- coding: utf-8 -*-

"""
    File name: bait.py
    Author: Canberk Özdemir
    Date created: 2/2/2019
    Date last modified: 2/2/2019
    Python version: 3.7

    Set or Get bait. Calculate user how far away from bait.
"""

import sqlite3 as sql
import datetime
import logging
import random
from geopy.distance import great_circle
from database import DatabaseGreyd


class Bait(DatabaseGreyd):
    """ Bait main class """

    def __init__(self, greyd_id, user_location, lobby_id, lobby_center_location,
                 bait_location):
        super(Bait, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.datetime.now())
        self.greyd_id = greyd_id
        self.user_location = user_location
        self.lobby_center_location = lobby_center_location
        self.lobby_id = lobby_id
        self.bait_location = bait_location

    def new_bait_location(self):
        """ Create new bait on map. """

        # TODO(canberk) Check random 100 999 is enough?
        longitude, latitude = self.lobby_center_location.split(",")
        new_longitude = longitude[:-3] + str(random.randint(100, 999))
        new_latitude = latitude[:-3] + str(random.randint(100, 999))
        new_bait_location = new_longitude + "," + new_latitude

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            cursor.execute("""UPDATE lobbies SET current_bait_location=?
                              WHERE lobby_id=?""",
                           (new_bait_location, self.lobby_id))
            database.commit()

        return new_bait_location

    def is_bait_taken(self):
        """ Calculate distance from user and bait. """

        circle = great_circle(self.user_location, self.bait_location).km
        return bool(circle < 0.01)
