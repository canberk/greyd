# -*- coding: utf-8 -*-

"""
    File name: user.py
    Author: Canberk Özdemir
    Date created: 2/2/2019
    Date last modified: 2/6/2019
    Python version: 3.7

    User get, set from database.
"""

import sqlite3 as sql
import logging
import datetime
from database import DatabaseGreyd


class User(DatabaseGreyd):
    """ User main class """

    def __init__(self, greyd_id, lobby_id, session_id):
        super(User, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.datetime.now())
        self.greyd_id = greyd_id
        self.lobby_id = lobby_id
        self.session_id = session_id

    def user_taken_bait(self):
        """ Add point for user. """

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            # Add 1 point total user score
            cursor.execute("""UPDATE user SET total_score = total_score + 1
                            WHERE greyd_id=?""", (self.greyd_id,))
            database.commit()

            # Find Game type is life or time ending?
            game_type = cursor.execute("""SELECT game_life_number FROM lobbies
                                        WHERE lobby_id=?""", (self.lobby_id,))

            if game_type[0] == 0:
                # Life index lobby ending.
                # Other users in lobby lost life points.
                cursor.execute("""UPDATE user_to_lobby
                                  SET remaining_life = 
                                  CASE WHEN greyd_id!=? AND remaining_life != 0
                                  THEN remaining_life - 1 END
                                  WHERE lobby_id=?""",
                               (self.greyd_id, self.lobby_id,))
                database.commit()

    def user_info_same_lobby(self, lobby_id):
        pass
