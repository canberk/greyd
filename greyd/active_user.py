# -*- coding: utf-8 -*-

"""
    File name: active_user.py
    Author: Canberk Özdemir
    Date created: 5/23/2018
    Date last modified: 1/24/2019
    Python version: 3.7

    Active user in game
    Greyd Rule: 1xx
"""

import sqlite3 as sql
import datetime
import logging
from database import DatabaseGreyd


class ActiveUser(DatabaseGreyd):
    """Active game greyd rules handler"""

    def __init__(self):
        super(ActiveUser, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.datetime.now())

    def entry(self, greyd_rule, json_request):
        """Desicion of request rotation for active user request"""
        if greyd_rule == 101:
            response = self.__game_active_user__(json_request)
        elif greyd_rule == 102:
            response = self.__refresh_lobby__(json_request)
        return response

    def __game_active_user__(self, json_request):
        """Return other lobby friends information in game"""
        # TODO(canberk) Game Active User absolutely empty
        pass

    def __refresh_lobby__(self, json_request):
        """Return other lobby friends information in lobby"""

        greyd_id = json_request["greydId"]
        lobby_id = json_request["lobbyId"]
        last_seen_chat_id = json_request["lastSeenChatId"]

        # User texted that request
        if "lobbyChat" in json_request.keys():
            with sql.connect(self.db_path) as database:
                # Get Session id
                cursor = database.cursor()

                session_id = cursor.execute("""SELECT session_id
                                                   FROM user_to_lobby
                                                   WHERE lobby_id=? and
                                                   greyd_id=?
                                                   """,
                                            (lobby_id, greyd_id,)).fetchone()

                # Add database how many different message in that request
                for chat_content in json_request["lobbyChat"]:
                    cursor.execute("""INSERT INTO lobbies_chat
                                      (session_id, chat_content, chat_time)
                                      VALUES (?,?,?)""",
                                   (session_id[0], chat_content,
                                    self.time_now,))
                    database.commit()

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

                users = cursor.execute("""SELECT user.full_name,
                                          user.greyd_id,
                                          user.facebook_id,
                                          user.total_score 
                                          FROM user 
                                          INNER JOIN user_to_lobby 
                                          ON user.greyd_id = user_to_lobby.greyd_id 
                                          WHERE lobby_id=?""",
                                       (lobby_id,)).fetchall()

                user_info_dict = []
                for user in users:
                    user_chat = []
                    user_info = {"userFullName": user[0], "userGreydId": user[1],
                                 "userFacebookId": int(user[2]), "userScore": user[3]}

                    chats = cursor.execute("""SELECT lobbies_chat.chat_time,
                                              lobbies_chat.chat_content 
                                              FROM lobbies_chat 
                                              INNER JOIN user_to_lobby 
                                              ON lobbies_chat.session_id=user_to_lobby.session_id
                                              WHERE  chat_id>? and 
                                              user_to_lobby.lobby_id=? and 
                                              lobbies_chat.session_id!=?""",
                                           (last_seen_chat_id, lobby_id,
                                            session_id[0])).fetchall()
                    for chat in chats:
                        chat_info = {
                            "chatTime": chat[0], "chatContent": chat[1]}
                        user_chat.append(chat_info)

                    user_info_dict.append(user_info)

                response["users"] = user_info_dict

        return response
