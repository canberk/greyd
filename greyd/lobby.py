# -*- coding: utf-8 -*-

"""
    File name: lobby.py
    Author: Canberk Özdemir
    Date created: 2/5/2018
    Date last modified: 1/22/2019
    Python version: 3.7.2

    Lobby operations on database and create response.
    Greyd Rule: 2xx
"""

import sqlite3 as sql
import logging
import datetime
import random
from geopy.distance import great_circle
from database import DatabaseGreyd


class LobbyTransaction(DatabaseGreyd):
    """ This class handle lobby transaction. """

    def __init__(self):
        super(LobbyTransaction, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.datetime.now())

    def entry(self, greyd_rule, json_request):
        """Decision which method to go for lobby."""
        if greyd_rule == 201:
            response = self.__create_lobby__(json_request)
        elif greyd_rule == 202:
            response = self.__find_lobby__(json_request)
        elif greyd_rule == 203:
            response = self.__join_lobby__(json_request)
        elif greyd_rule == 204:
            response = self.__start_game__(json_request)
        elif greyd_rule == 205:
            response = self.__leave_lobby__(json_request)
        return response

    def __create_lobby__(self, json_request):
        """Lobby creater and add database."""

        greyd_id = json_request["greydId"]
        lobby_name = json_request["lobbyName"]
        lobby_distance = json_request["lobbyDistance"]
        game_max_time = json_request["gameMaxTime"]
        game_max_life = json_request["gameMaxLife"]
        center_location = json_request["lobbyCenterLocation"]

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            cursor.execute("""
            INSERT INTO lobbies 
            (lobby_owner_greyd_id,
             lobby_center_location,
             lobby_name,
             game_distance,
             lobby_setup_time,
             game_life_number,
             game_max_time
            )
            VALUES (?,?,?,?,?,?,?)
            """, (greyd_id, center_location, lobby_name, lobby_distance,
                  self.time_now, game_max_life, game_max_time,))
            database.commit()

            lobby = cursor.execute(
                """SELECT max(lobby_id),lobby_status FROM lobbies""").fetchone()

            lobby_id = lobby[0]
            lobby_status = lobby[1]

            cursor.execute("""
            INSERT INTO user_to_lobby
            (lobby_id, greyd_id,
             user_lobby_entry_time
            )
            VALUES (?,?,?)
            """, (lobby_id, greyd_id, self.time_now,))
            database.commit()

        response = {"success": True, "greydRule": 201, "lobbyId": lobby_id,
                    "lobbyStatus": lobby_status}
        self.logger.info("Create new lobby Name: %s lobbyId: %s", lobby_name,
                         lobby_id)
        return response

    def __find_lobby__(self, json_request):
        """Find lobbies around the user."""

        greyd_id = json_request["greydId"]
        user_location = json_request["location"]

        response = {"success": True, "greydRule": 202}

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            # find lobby active and near to user
            lobbies = cursor.execute("""
            SELECT lobby_id,
                   lobby_name,
                   lobby_owner_greyd_id,
                   user.full_name,
                   user.facebook_id,
                   game_max_time,
                   game_life_number,
                   game_distance, 
                   lobby_center_location
            FROM lobbies
            inner join user on 
                user.greyd_id = lobbies.lobby_owner_greyd_id
            WHERE 
                user.location_city = (
                SELECT location_city 
                FROM user
                WHERE greyd_id = ?
                )
            """, (greyd_id,)).fetchall()

            json_list = []
            for i in lobbies:
                circle = great_circle(i[8], user_location).km
                # If same city and lobby in 2 kilometer
                if circle < 2:
                    result_dict = {"lobbyId": i[0], "lobbyName": i[1],
                                   "lobbyCreatorGreydId": i[2],
                                   "lobbyCreatorFullName": i[3],
                                   "lobbyCreatorFacebookId": i[4],
                                   "gameMaxTime": i[5], "gameMaxLife": i[6],
                                   "lobbyGameDistance": i[7],
                                   "lobbyCenterLocation": i[8]}
                    json_list.append(result_dict)

        response["lobbies"] = json_list
        return response

    def __join_lobby__(self, json_request):
        """User join the lobby."""

        greyd_id = json_request["greydId"]
        lobby_id = json_request["lobbyId"]

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            cursor.execute("""
            INSERT INTO user_to_lobby
             (lobby_id,
              greyd_id,
              user_lobby_entry_time,
              remaining_life
             )
            VALUES (?,?,?,
                (SELECT game_life_number
                 FROM lobbies
                 WHERE lobby_id=?
                 )
            )
            """, (lobby_id, greyd_id, self.time_now, lobby_id,))
            database.commit()

            # TODO(canberk) Total score getting and add response json
            users = cursor.execute("""
            SELECT user_to_lobby.greyd_id,
                   user.facebook_id
            FROM user_to_lobby
            INNER JOIN user
            ON user.greyd_id = user_to_lobby.greyd_id
            WHERE lobby_id=?
            """, (lobby_id,)).fetchall()
            json_list = []
            for i in users:
                json_list.append({"userGreydId": i[0], "userFacebookId": i[1]})

        response = {"success": True, "greydRule": 203,
                    "greydId": greyd_id, "lobbyId": lobby_id, "lobbies": json_list}
        return response

    def __start_game__(self, json_request):
        """Lobby creator start the game and first bait users will be notified"""

        greyd_id = json_request["greydId"]
        lobby_id = json_request["lobbyId"]
        response = {"greydRule": 204}

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            lobby_info = cursor.execute("""
            SELECT lobby_owner_greyd_id,
                   lobby_status,
                   lobby_center_location
            FROM lobbies 
            WHERE lobby_id=?
            """, (lobby_id,)).fetchone()

            if greyd_id == lobby_info[0]:
                response["success"] = True
                response["lobbyId"] = lobby_id
                response["lobbyStatus"] = 1
                # First bait create
                # TODO(canberk) Check random 100 999 is enough?
                longitude, latitude = lobby_info[2].split(",")
                new_longitude = longitude[:-3] + str(random.randint(100, 999))
                new_latitude = latitude[:-3] + str(random.randint(100, 999))
                bait = new_longitude + "," + new_latitude
                cursor.execute("""
                UPDATE lobbies 
                SET lobby_status=?, 
                    game_start_time=?,
                current_bait_location=? WHERE lobby_id=?
                """, (1, self.time_now, bait, lobby_id,))
                response["firstBaitLocation"] = bait
                self.logger.info(
                    "Lobby started the game LobbyId: %s", lobby_id)

            else:
                response["success"] = False

        return response

    def __leave_lobby__(self, json_request):
        """User quit the lobby"""

        greyd_id = json_request["greydId"]
        lobby_id = json_request["lobbyId"]

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            # Is lobby creator?
            lobby_info = cursor.execute("""
            SELECT lobby_owner_greyd_id, 
                   lobby_status 
            FROM lobbies
            WHERE lobby_id=?
            """, (lobby_id,)).fetchone()
            # Close lobby
            if lobby_id == lobby_info[0] and lobby_info[1] == 1:
                # TODO(canberk) Find the game winner and proccess and building user_location table
                cursor.execute("""
                UPDATE lobbies 
                SET game_end_time=?, 
                    lobby_status=?
                WHERE lobby_id=?
                """, (self.time_now, 2, lobby_id,))

                cursor.execute("""
                UPDATE user_to_lobby 
                SET user_lobby_exit_time=?
                WHERE lobby_id=?
                """, (self.time_now, lobby_id,))
                log = "Lobby {} terminated by greydId: {}".format(
                    lobby_id, greyd_id)
                self.logger.info(log)
            # if person is normal user
            else:
                cursor.execute("""
                UPDATE user_to_lobby 
                SET user_lobby_exit_time=?
                WHERE lobby_id=? and greyd_id=?
                """, (self.time_now, lobby_id, greyd_id,))
                database.commit()

        response = {"success": True, "greydRule": 205, "greydId": greyd_id,
                    "lobbyId": lobby_id}
        return response
