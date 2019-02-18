# -*- coding: utf-8 -*-

"""Active user in game.
Greyd Rule: 1xx
"""

import logging
from datetime import datetime, timedelta

from greyd.db import session
from greyd.models.user import User
from greyd.models.lobby import Lobby
from greyd.models.user_to_lobby import UserToLobby
from greyd.models.chat import Chat
from greyd.models.user_location import UserLocation


class ActiveUser():
    """Active game greyd rules handler.
    This class contains user transaction on game.
    Decide of game rotation (continue, finish) with request data.
    If game finish regular ways then find winnner user.
    """
    logger = logging.getLogger(__name__)

    def __init__(self, request):
        self.request = request
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.now())
        self.session_id = self._get_session_id()
        self.lobby = self._get_lobby()

    def entry(self):
        """Decide of the game request way. Response json.

        Greyd Rule  -   Entry Style
            101     -   User on a game.
            102     -   User wait in the lobby.
        """
        greyd_rule = self.request["greydRule"]
        if greyd_rule == 101:
            response = self._refresh_game()
        elif greyd_rule == 102:
            response = self._refresh_lobby()
        else:
            error_type = "Wrong greyRule Game request."
            response = {"success": False, "errorType": error_type}
            self.logger.error("%s GreydId: %s", error_type,
                              self.request["greydId"])
        return response

    def _refresh_game(self):
        """Use user location, is taken bait or not?
        If user is lobby owner then check is game end?
        Return other lobby users information(chat, users.id etc.) in game.
        """
        self._add_chat()

        if self.lobby.is_bait_taken(self.request["location"]):
            self._points_inc_dec()
            bait_taken = True
        else:
            bait_taken = False

        location = UserLocation(session_id=self.session_id,
                                location=self.request["location"],
                                time=self.time_now,
                                bait_location=self.lobby.bait_location,
                                is_bait_taken=bait_taken)
        session.add(location)
        session.commit()

        # Check game is end or continue.
        self._is_game_end()

        return {"success": True,
                "greydRule": self.request["greydRule"],
                "greydId": self.request["greydId"],
                "lobbyId": self.lobby.id,
                "currentBaitLocation": self.lobby.bait_location,
                "lobbyStatus": self.lobby.status,
                "users": self._user_info_same_lobby()}

    def _refresh_lobby(self):
        """Use Chat request and return other users chat information."""
        self._add_chat()

        if self.lobby.bait_location is None:
            bait_location = ""
        else:
            bait_location = self.lobby.bait_location

        return {"success": True,
                "greydRule": self.request["greydRule"],
                "greydId": self.request["greydId"],
                "lobbyId": self.request["lobbyId"],
                "lobbyStatus": self.lobby.status,
                "baitLocation": bait_location,
                "users": self._user_info_same_lobby()}

    def _get_lobby(self):
        """Return lobby."""
        return session.query(Lobby).filter(
            Lobby.id == self.request["lobbyId"]).first()

    def _get_session_id(self):
        """Return session id."""
        return session.query(UserToLobby.id).filter(
            UserToLobby.lobby_id == self.request["lobbyId"]).filter(
                UserToLobby.user_id == self.request["greydId"]).first()[0]

    def _add_chat(self):
        """Add database chat content."""
        if "lobbyChat" in self.request.keys():
            for chat_content in self.request["lobbyChat"]:
                chat = Chat(session_id=self.session_id,
                            content=chat_content,
                            time=self.time_now)
                session.add(chat)
            session.commit()

    def _user_info_same_lobby(self):
        """Get other users info and chat info."""

        lobby_users = session.query(UserToLobby).join(UserToLobby.user).filter(
            UserToLobby.lobby_id == self.request["lobbyId"]).all()

        user_list = []
        for lobby_user in lobby_users:
            # Find how many taken bait in this lobby.
            user_taken_bait = session.query(UserLocation).filter(
                UserLocation.session_id == lobby_user.id).filter(
                    UserLocation.is_bait_taken).count()

            user_info = {"userGreydId": lobby_user.user.id,
                         "userFacebookId": lobby_user.user.facebook_id,
                         "userFullName": lobby_user.user.full_name,
                         "userScore": lobby_user.user.total_score,
                         "userLocation": lobby_user.user.location,
                         "userTotalBait": user_taken_bait}

            # Add chat data in response
            chats = session.query(Chat).filter(
                Chat.session_id == lobby_user.id).filter(
                    Chat.id > self.request["lastSeenChatId"]).all()

            user_chat = []
            for chat in chats:
                chat_info = {"chatId": chat.id,
                             "chatTime": chat.time,
                             "chatContent": chat.content}
                user_chat.append(chat_info)

            user_list.append(user_info)
        return user_list

    def _game_result(self):
        """Game Result. Find winner user."""
        self.lobby.end_game()
        winner_session = session.query(UserToLobby).order_by(
            UserToLobby.collected_bait.desc()).first()
        winner_session.is_game_won = True
        session.commit()

    def _is_game_end(self):
        """Control of game. Control authorization only lobby creator."""
        if self.lobby.creator_id != self.request["greydId"]:
            return

        # Check time ending
        start_time = datetime.strptime(self.lobby.start_time, '%m/%d/%Y %H:%M')
        expecting_end_time = start_time + \
            timedelta(minutes=self.lobby.max_time)

        if expecting_end_time <= datetime.now():
            self._game_result()

        # Check life ending
        # How many user have more than 0 life
        user_still_playing = session.query(UserToLobby).filter(
            UserToLobby.lobby_id == self.lobby.id).filter(
                UserToLobby.remaining_life > 0).count()
        if user_still_playing < 0:
            self._game_result()

    def _points_inc_dec(self):
        """Add 1 point for bait taken user and other user lost 1 life."""
        user = session.query(User).filter(
            User.id == self.request["greydId"]).first()
        user.add_point()

        users_session = session.query(UserToLobby).filter(
            UserToLobby.lobby_id == self.lobby.id).filter(
                UserToLobby.remaining_life > 0).all()

        for user_session in users_session:
            # User is won the bait then increase the collected bait
            # else then user lose the life.
            if user_session.id == self.session_id:
                user_session.collected_bait = user_session.collected_bait + 1
            else:
                user_session.remaining_life = user_session.remaining_life - 1
            session.commit()
