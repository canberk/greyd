# -*- coding: utf-8 -*-

"""
    User statistics module.
    Greyd Rule: 3xx
"""

import sqlite3 as sql
import logging
from datetime import datetime
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

        greyd_id = json_request["greydId"]

        response = {"success": True,
                    "greydRule": 302,
                    "greydId": greyd_id,
                    "totalScore": self.__get_total_score__(greyd_id),
                    "totalWalkDistance": self.__find_distance__(greyd_id),
                    "collectedBait": self.__get_collected_bait__(greyd_id)}
        response.update(self.__past_game_infos__(greyd_id))

        return response

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

    def __get_total_score__(self, greyd_id):
        """Get total user score."""
        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            score = cursor.execute("""SELECT total_score FROM user
                                   WHERE greyd_id=?""", (greyd_id,)).fetchone()

            return score[0]

    def __past_game_infos__(self, greyd_id):
        """Total game time, total game, collected bait and won game.
        Return dict."""

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            games = cursor.execute("""SELECT user_lobby_entry_time,
                                   user_lobby_exit_time,
                                   is_game_won 
                                   FROM user_to_lobby 
                                   WHERE greyd_id=?""", (greyd_id,)).fetchall()

        time_format = "%m/%d/%Y %H:%M"
        total_time = 0
        total_game = 0
        won_game = 0
        for game in games:
            total_game += 1

            if game[2] == 1:
                won_game += 1

            entry_time = datetime.strptime(game[0], time_format)
            exit_time = datetime.strptime(game[1], time_format)

            if entry_time < exit_time:
                time_diff = exit_time - entry_time
                time_diff = int(time_diff.total_seconds())
                total_time += time_diff

        infos = {"totalGame": total_game,
                 "totalGameTime": total_time,
                 "wonGame": won_game}
        return infos

    def __get_collected_bait__(self, greyd_id):
        """Return collected bait number."""
        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            bait_number = cursor.execute("""SELECT COUNT(*)
                                         FROM user_location 
                                         WHERE is_bait_taken=1 AND 
                                         session_id in (SELECT session_id
                                                        FROM user_to_lobby
                                                        WHERE greyd_id=?)""",
                                         (greyd_id,)).fetchone()

        return bait_number[0]
