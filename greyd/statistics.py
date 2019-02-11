# -*- coding: utf-8 -*-

"""
    User statistics module.
    Greyd Rule: 3xx
"""

import sqlite3 as sql
import logging
from geopy.distance import distance
from database import DatabaseGreyd


class UserStatistics(DatabaseGreyd):
    """User statistics information."""

    def __init__(self):
        super(UserStatistics, self).__init__()
        self.logger = logging.getLogger(__name__)

    def entry(self, greyd_rule, json_request):
        """Desicion statistic/score information to world,friends,city"""
        if greyd_rule == 301:
            response = self.__get_score__(json_request)
        elif greyd_rule == 302:
            response = self.__get_statistics__(json_request)
        return response

    def __get_score__(self, json_request):
        """Return score information."""

        greyd_id = json_request["greydId"]
        friends_facebook_ids = json_request["friendsFacebookId"]

        response = {"success": True,
                    "greydRule": 301,
                    "greydId": greyd_id,
                    "world": self.__get_top_players__(),
                    "city": self.__get_top_players__(greyd_id),
                    "facebookFriends":
                    self.__get_friends_statics__(friends_facebook_ids)}

        return response

    def __get_statistics__(self, json_request):
        """Return statistics information."""
        pass

    def __get_top_players__(self, city_greyd_id=0, number_of_players=10):
        """Get information of the top n players (default=10).
            Return that data in dict."""

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            if city_greyd_id == 0:
                # World top n list
                users = cursor.execute("""SELECT greyd_id, facebook_id,
                                       full_name, total_score FROM user 
                                       ORDER BY total_score DESC LIMIT ?""",
                                       (number_of_players,)).fetchall()
            else:
                # Same city top n list
                users = cursor.execute("""SELECT greyd_id, facebook_id,
                                       full_name, total_score, location 
                                       FROM user 
                                       WHERE location_city=(SELECT location_city
                                                            FROM user
                                                            WHERE greyd_id=?)
                                       ORDER BY total_score DESC LIMIT ?""",
                                       (city_greyd_id,
                                        number_of_players,)).fetchall()

            users_info_dict = []
            for user in users:
                user_greyd_id = user[0]

                user_distance = self.__find_distance__(user_greyd_id)
                user_info = {"userGreydId": user[0],
                             "userFacebookId": user[1],
                             "userFullName": user[2],
                             "userTotalScore": user[3],
                             "userWalkingDistance": user_distance}

                users_info_dict.append(user_info)

        return users_info_dict

    def __get_friends_statics__(self, facebook_ids):
        """Facebook friends information."""

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            friends = cursor.execute("""SELECT greyd_id, facebook_id,
                                          full_name, total_score 
                                          FROM user
                                          WHERE facebook_id IN (%s)""" %
                                     ','.join('?'*len(facebook_ids)),
                                     facebook_ids).fetchall()

            users_info_dict = []
            for user in friends:
                user_greyd_id = user[0]

                user_distance = self.__find_distance__(user_greyd_id)
                user_info = {"userGreydId": user[0],
                             "userFacebookId": user[1],
                             "userFullName": user[2],
                             "userTotalScore": user[3],
                             "userWalkingDistance": user_distance}

                users_info_dict.append(user_info)

        return users_info_dict

    def __find_distance__(self, greyd_id):
        """Calculate user how many meter walk on game history."""

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            locations = cursor.execute("""SELECT user_location.session_id,
                                           user_location.user_location
                                           FROM user_location 
                                           INNER JOIN user_to_lobby
                                           ON user_location.session_id=user_to_lobby.session_id
                                           WHERE user_to_lobby.greyd_id=?
                                           ORDER BY user_location.session_id
                                           ASC""",
                                       (greyd_id,)).fetchall()

            user_distance = 0
            for location1, location2 in zip(locations, locations[1:]):
                if location1[0] == location2[0]:
                    user_distance += distance(location1[1], location2[1]).m

        return user_distance
