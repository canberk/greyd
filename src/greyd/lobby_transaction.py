# -*- coding: utf-8 -*-

"""Lobby operations on database and create response.
Greyd Rule: 2xx
"""

import logging
from datetime import datetime
from geopy.distance import great_circle

from greyd.db import session
from greyd.models.lobby import Lobby
from greyd.models.user import User
from greyd.models.user_to_lobby import UserToLobby


class LobbyTransaction():
    """Lobby Main Class."""
    logger = logging.getLogger(__name__)

    def __init__(self, request):
        self.request = request
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.now())

    def entry(self):
        """Decide of the lobby request way. Response json.

        Greyd Rule  -   Entry Style
            201     -   Create Lobby
            202     -   Find Lobbies
            203     -   Join Lobby
            204     -   Start Game
            205     -   Leave Lobby
        """
        greyd_rule = self.request["greydRule"]
        if greyd_rule == 201:
            response = self._create_lobby()
        elif greyd_rule == 202:
            response = self._find_lobby()
        elif greyd_rule == 203:
            response = self._join_lobby()
        elif greyd_rule == 204:
            response = self._start_game()
        elif greyd_rule == 205:
            response = self._leave_lobby()
        else:
            error_type = "Wrong greyRule Lobby request."
            response = {"success": False, "errorType": error_type}
            self.logger.error("%s GreydId: %s", error_type,
                              self.request["greydId"])
        return response

    def _create_lobby(self):
        """Lobby creator method."""
        lobby = Lobby(creator_id=self.request["greydId"],
                      center_location=self.request["lobbyCenterLocation"],
                      name=self.request["lobbyName"],
                      game_distance=self.request["lobbyDistance"],
                      setup_time=self.time_now,
                      life_number=self.request["gameMaxLife"],
                      max_time=self.request["gameMaxTime"])
        session.add(lobby)
        session.commit()

        self.logger.info("New lobby created. LobbyId: %s, Creator GreydId: %s",
                         lobby.id, lobby.creator_id)

        # Add session for new lobby.
        self.request["lobbyId"] = lobby.id
        self._join_lobby()

        return {"success": True,
                "greydRule": self.request["greydRule"],
                "lobbyId": lobby.id,
                "lobbyStatus": lobby.status}

    def _find_lobby(self):
        """Find lobbies around the user."""
        user = session.query(User).filter(
            User.id == self.request["greydId"]).first()

        lobbies = session.query(Lobby).join(Lobby.creator_user).filter(
            User.city == user.city).all()

        lobby_list = []
        for lobby in lobbies:
            # If same city and lobby in 2 kilometer add list.
            circle = great_circle(lobby.center_location, user.location)
            if circle < 2:
                lobby_info = {"lobbyId": lobby.id,
                              "lobbyName": lobby.name,
                              "lobbyCreatorGreydId": lobby.creator_id,
                              "lobbyCreatorFullName": lobby.creator_user.full_name,
                              "lobbyCreatorFacebookId": lobby.creator_user.facebook_id,
                              "gameMaxTime": lobby.max_time,
                              "gameMaxLife": lobby.life_number,
                              "lobbyGameDistance": lobby.game_distance,
                              "lobbyCenterLocation": lobby.center_location}
                lobby_list.append(lobby_info)

        return {"success": True,
                "greydRule": self.request["greydRule"],
                "lobbies": lobby_list}

    def _join_lobby(self):
        """User join the lobby proccess."""
        lobby = session.query(Lobby).filter(
            Lobby.id == self.request["lobbyId"]).first()

        lobby_session = UserToLobby(lobby_id=self.request["lobbyId"],
                                    user_id=self.request["greydId"],
                                    entry_time=self.time_now,
                                    remaining_life=lobby.life_number)
        session.add(lobby_session)
        session.commit()
        self.logger.info("GreydId: %s joined the lobby. LobbyId: %s",
                         self.request["greydId"], lobby.id)

        lobby_users = session.query(UserToLobby).join(UserToLobby.user).filter(
            UserToLobby.lobby_id == lobby_session.lobby_id).all()

        user_list = []
        for lobby_user in lobby_users:
            user_list.append({"userGreydId": lobby_user.user.id,
                              "userFacebookId": lobby_user.user.facebook_id})

        return {"success": True,
                "greydRule": self.request["greydRule"],
                "greydId": self.request["greydId"],
                "lobbyId": lobby.id,
                "users": user_list}

    def _start_game(self):
        """Lobby creator start the game and first bait users will be
        notified.
        """
        lobby = session.query(Lobby).filter(
            Lobby.id == self.request["lobbyId"]).first()

        # Add remaining life all lobby users.
        users = session.query(UserToLobby).filter(
            UserToLobby.lobby == lobby).all()
        for user in users:
            user.remaining_life = lobby.life_number
        session.commit()

        # Has user permission on the lobby?
        if self.request["greydId"] == lobby.creator_id:  # noqa pylint: disable=no-else-return
            lobby.start_game()
            self.logger.info("Game Started LobbyId: %s", lobby.id)
            return {"success": True,
                    "greydId": self.request["greydId"],
                    "greydRule": self.request["greydRule"],
                    "lobbyId": lobby.id,
                    "lobbyStatus": lobby.status,
                    "firstBaitLocation": lobby.bait_location}
        else:
            self.logger.warning(
                "Unauthorized start game request. GreydId: %s, LobbyId: %s",
                self.request["greydId"], lobby.id)
            return {"success": False,
                    "errorType": "Unauthorized request"}

    def _leave_lobby(self):
        """User quit the lobby"""
        lobby = session.query(Lobby).filter(
            Lobby.id == self.request["lobbyId"]).first()

        # Is lobby creator?
        if self.request["greydId"] == lobby.creator_id:
            lobby.end_game()
            # All session is terminating.
            users_session = session.query(UserToLobby).filter(
                UserToLobby.lobby_id == lobby.id).all()
            users_session.exit_time = self.time_now
            self.logger.info(
                "The lobby owner ended the lobby. LobbyId: %s", lobby.id)
            winner_session = session.query(UserToLobby).order_by(
                UserToLobby.collected_bait.desc()).first()
            winner_session.is_game_won = True
            session.commit()
        else:
            lobby_session = session.query(UserToLobby).filter(
                UserToLobby.lobby_id == self.request["lobbyId"]).filter(
                    UserToLobby.user_id == self.request["greydId"]).first()

            lobby_session.exit_time = self.time_now
            lobby_session.is_game_won = False
            self.logger.info("User left the lobby. GreydId: %s",
                             self.request["greydId"])

        session.commit()

        return {"success": True,
                "greydRule": self.request["greydRule"],
                "greydId": self.request["greydId"],
                "lobbyId": lobby.id}
