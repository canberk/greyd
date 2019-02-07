# -*- coding: utf-8 -*-

"""
    File name: active_user.py
    Author: Canberk Özdemir
    Date created: 5/23/2018
    Date last modified: 2/6/2019
    Python version: 3.7

    Active user in game
    Greyd Rule: 1xx
"""

import sqlite3 as sql
from datetime import datetime, timedelta
import logging
from user import User
from bait import Bait
from database import DatabaseGreyd


class ActiveUser(DatabaseGreyd):
    """Active game greyd rules handler"""

    def __init__(self):
        super(ActiveUser, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.now())

    def entry(self, greyd_rule, json_request):
        """Desicion of request rotation for active user request"""
        if greyd_rule == 101:
            response = self.__game_active_user__(json_request)
        elif greyd_rule == 102:
            response = self.__refresh_lobby__(json_request)
        return response

    def __game_active_user__(self, json_request):
        """Return other lobby friends information in game"""

        greyd_id = json_request["greydId"]
        lobby_id = json_request["lobbyId"]
        location = json_request["location"]
        last_seen_chat_id = json_request["lastSeenChatId"]

        session_id = self.__get_session_id__(greyd_id, lobby_id)

        if "lobbyChat" in json_request.keys():
            self.__chat_add__(session_id, json_request["lobbyChat"])

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            lobby = cursor.execute("""SELECT lobby_owner_greyd_id,
                                    lobby_center_location,
                                    current_bait_location
                                    FROM lobbies WHERE lobby_id=?
                                    """, (lobby_id,)).fetchone()

            lobby_owner_greyd_id = lobby[0]
            lobby_center_location = lobby[1]
            bait_location = lobby[2]

            user = User(greyd_id, lobby_id, session_id)
            bait = Bait(greyd_id, location, lobby_id,
                        lobby_center_location, bait_location)

            # If user taken bait
            if bait.is_bait_taken():
                user.user_taken_bait()
                bait_location = bait.new_bait_location()
                bait_taken = 1
            else:
                bait_taken = 0

            # New location for user on database.
            cursor.execute("""INSERT INTO user_location
                          (session_id,
                          bait_location,
                          user_location,
                          is_bait_taken) 
                          VALUES (?,?,?,?)""",
                           (session_id, bait_location, location,
                            bait_taken,))
            database.commit()

            # Check is game end?
            if (greyd_id == lobby_owner_greyd_id and
                    self.__is_lobby_end__(lobby_id)):
                self.__game_result__(lobby_id)

            response = {"success": True, "greydRule": 101, "greydId":
                        greyd_id, "lobbyId": lobby_id,
                        "currentBaitLocation": bait_location}

            lobby_status = cursor.execute("""SELECT lobby_status FROM lobbies
                                  WHERE lobby_id=?""",
                                          (lobby_id,)).fetchone()
            response["lobbyStatus"] = lobby_status[0]

            # user bait history in this lobby
            user_bait = cursor.execute("""SELECT count(*) FROM user_location
                                        WHERE session_id=?""",
                                       (session_id,)).fetchone()
            response["totalBait"] = user_bait[0]
            response["totalScore"] = user_bait[0]
            response["users"] = self.__user_info_same_lobby__(
                lobby_id, session_id, last_seen_chat_id)

        return response

    def __refresh_lobby__(self, json_request):
        """Return other lobby friends information in lobby"""

        greyd_id = json_request["greydId"]
        lobby_id = json_request["lobbyId"]
        last_seen_chat_id = json_request["lastSeenChatId"]

        session_id = self.__get_session_id__(greyd_id, lobby_id)

        if "lobbyChat" in json_request.keys():
            self.__chat_add__(session_id, json_request["lobbyChat"])

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            # Set return json data Lobby, user, chat information
            response = {"success": True, "greydRule": 102, "greydId":
                        greyd_id, "lobbyId": lobby_id}

            lobby_info = cursor.execute("""SELECT lobby_status,
                                        current_bait_location 
                                        FROM lobbies WHERE lobby_id=?
                                        """, (lobby_id,)).fetchone()
            response["lobbyStatus"] = lobby_info[0]

            # If lobby creator started the game
            if lobby_info[1] is None:
                response["baitLocation"] = ""
            else:
                response["baitLocation"] = lobby_info[1]

            response["users"] = self.__user_info_same_lobby__(
                lobby_id, session_id, last_seen_chat_id)

        return response

    def __chat_add__(self, session_id, chat_messages):
        """Add database chat content"""

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            # Add database how many different message in that request
            for chat_content in chat_messages:
                cursor.execute("""INSERT INTO lobbies_chat
                                    (session_id, chat_content, chat_time)
                                    VALUES (?,?,?)""",
                               (session_id, chat_content, self.time_now,))
                database.commit()

    def __get_session_id__(self, greyd_id, lobby_id):
        """ Get session id from database """

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            session_id = cursor.execute("""SELECT session_id
                                                        FROM user_to_lobby
                                                        WHERE lobby_id=? and
                                                        greyd_id=?
                                                        """,
                                        (lobby_id, greyd_id,)).fetchone()

        return session_id[0]

    def __is_lobby_end__(self, lobby_id):
        """ Check lobby is end or not. """

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            lobby_info = cursor.execute("""SELECT game_start_time,
                                        game_life_number,
                                        game_max_time
                                        FROM lobbies 
                                        WHERE lobby_id=?""",
                                        (lobby_id,)).fetchone()

        game_start_time = lobby_info[0]
        game_life_number = lobby_info[1]
        game_max_time = lobby_info[2]

        # TODO Change database time format d/m/y to m/d/y
        # Calculate time ending
        if game_max_time != 0:
            game_start_time = datetime.strptime(
                game_start_time, '%d/%m/%Y %H:%M')

            expecting_game_end_time = game_start_time + \
                timedelta(minutes=game_max_time)

            if datetime.now() <= expecting_game_end_time:
                return True

        # Only 1 or less(bug) user has life
        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            user_still_playing = cursor.execute("""SELECT COUNT(*)
                                                FROM user_to_lobby
                                                WHERE remaining_life>0 and
                                                lobby_id=?""", (lobby_id,))

            if user_still_playing[0] < 2:
                return True
        return False

    def __game_result__(self, lobby_id):
        """ End of game """

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            # Find winner user greydId
            # Count users how many taken bait through user location history
            winner_user = cursor.execute("""SELECT greyd_id, session_id,
                                            MAX(is_bait_taken) 
                                            FROM (select user_to_lobby.greyd_id,
                                            user_location.session_id,
                                            COUNT(*) as is_bait_taken
                                            FROM user_location
                                            INNER JOIN user_to_lobby
                                            ON user_to_lobby.session_id = user_location.session_id
                                            WHERE is_bait_taken > 0 and
                                            user_to_lobby.lobby_id=?
                                            GROUP BY user_location.session_id
                                            )""", (lobby_id,)).fetchone()

            # Lobby Status=2 mean finished game.
            cursor.execute("""UPDATE lobbies SET lobby_status=?,
                              winner_greyd_id=?
                              WHERE lobby_id=?""",
                           (2, winner_user[0], lobby_id,))

            cursor.execute("""UPDATE user_to_lobby SET is_game_won=?
                          WHERE session_id=?""", (1, winner_user[1]))
            database.commit()

    def __user_info_same_lobby__(self, lobby_id, session_id, last_seen_chat_id):
        """ GET user and chat info """

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            # TODO location using on user table change to user_location.user_location

            users = cursor.execute("""SELECT user.full_name,
                                        user.greyd_id,
                                        user.facebook_id,
                                        user.total_score,
                                        user.location,
                                        user_to_lobby.session_id
                                        FROM user 
                                        INNER JOIN user_to_lobby 
                                        ON user.greyd_id=user_to_lobby.greyd_id 
                                        WHERE user_to_lobby.lobby_id=?""",
                                   (lobby_id,)).fetchall()

            user_info_dict = []
            for user in users:

                # Find how many bait taken
                user_session_id = user[5]
                user_taken_bait = cursor.execute("""SELECT
                                                    COUNT(*) as is_bait_taken
                                                    FROM user_location
                                                    WHERE is_bait_taken > 0 and
											        session_id=?""",
                                                 (user_session_id,)).fetchone()

                user_chat = []
                user_info = {"userFullName": user[0], "userGreydId": user[1],
                             "userFacebookId": user[2], "userScore": user[3],
                             "userLocation": user[4],
                             "userTotalBait": user_taken_bait[0]}

                chats = cursor.execute("""SELECT lobbies_chat.chat_time,
                                                lobbies_chat.chat_content 
                                                FROM lobbies_chat 
                                                INNER JOIN user_to_lobby 
                                                ON lobbies_chat.session_id=user_to_lobby.session_id
                                                WHERE chat_id>? and 
                                                user_to_lobby.lobby_id=? and 
                                                lobbies_chat.session_id!=?""",
                                       (last_seen_chat_id, lobby_id,
                                        session_id)).fetchall()
                for chat in chats:
                    chat_info = {
                        "chatTime": chat[0], "chatContent": chat[1]}
                    user_chat.append(chat_info)

                user_info_dict.append(user_info)

        return user_info_dict
