# -*- coding: utf-8 -*-

"""User statistics module.
Greyd Rule: 3xx
"""

import logging
from datetime import datetime

from greyd.db import session
from greyd.models.user import User
from greyd.models.user_to_lobby import UserToLobby
from greyd.models.user_location import UserLocation


class UserStatistics():
    """User statistics information."""

    logger = logging.getLogger(__name__)

    def __init__(self, request):
        self.request = request
        self.user = session.query(User).filter(
            User.id == self.request["greydId"]).first()

    def entry(self):
        """Decide of the game request way. Response json.

        Greyd Rule  -   Entry Style
            301     -   Get Score of Friends, Same city, World
            302     -   User Statistics.
        """
        greyd_rule = self.request["greydRule"]
        if greyd_rule == 301:
            response = self._get_score()
        elif greyd_rule == 302:
            response = self._get_statistics()
        return response

    def _get_score(self):
        return {"success": True,
                "greydId": self.request["greydId"],
                "greydRule": self.request["greydRule"],
                "world": self._get_top_players(),
                "city": self._get_top_city_players(),
                "facebookFriends": self._get_facebook_friends_players()}

    def _get_statistics(self):
        response = {"success": True,
                    "greydRule": self.request["greydRule"],
                    "greydId": self.request["greydId"],
                    "totalScore": self.user.total_score,
                    "totalWalkDistance":
                    self.played_distance(self.request["greydId"])}
        response.update(self.played_games_info(self.request["greydId"]))
        return response

    def _get_top_players(self, number_of_player=10):
        """Get information of the top n players (default=10)."""
        users = session.query(User).order_by(User.total_score.desc()).limit(
            number_of_player).all()
        return self._user_info(users)

    def _get_top_city_players(self, number_of_player=10):
        users = session.query(User).filter(
            User.city == self.user.city).order_by(
                User.total_score.desc()).limit(number_of_player).all()
        return self._user_info(users)

    def _get_facebook_friends_players(self):
        friends_facebook_ids = self.request["friendsFacebookId"]
        friends = session.query(User).filter(User.id.in_(
            friends_facebook_ids)).all()
        return self._user_info(friends)

    def _user_info(self, users):
        user_info = []
        for user in users:
            user_info.append({"userGreydId": user.id,
                              "userFacebookId": user.facebook_id,
                              "userFullName": user.full_name,
                              "userTotalScore": user.total_score,
                              "userWalkingDistance":
                              self.played_distance(user.id)})
        return user_info

    @staticmethod
    def played_distance(greyd_id):
        """Calculate user how many meter walk on game history."""
        from geopy.distance import distance

        locations = session.query(UserLocation).join(UserToLobby).filter(
            UserLocation.session_id == UserToLobby.id).filter(
                UserToLobby.user_id == greyd_id).order_by(
                    UserLocation.session_id.asc()).all()

        user_distance = 0
        for location1, location2 in zip(locations, locations[1:]):
            if location1[0] == location2[0]:
                user_distance += distance(location1[1], location2[1]).m

        return user_distance

    @staticmethod
    def played_games_info(greyd_id):
        """Information about past games of users. Total game number, game time
        and how many won game.
        """
        sessions = session.query(UserToLobby).filter(
            UserToLobby.user_id == greyd_id).all()

        game_number = game_time = game_won = 0
        for game in sessions:
            game_number += 1

            if game.is_game_won:
                game_won += 1

            time_format = '%m/%d/%Y %H:%M'
            entry_time = datetime.strptime(game.entry_time, time_format)
            exit_time = datetime.strptime(game.exit_time, time_format)
            if entry_time < exit_time:
                time_diff = exit_time - entry_time
                time_diff = int(time_diff.total_seconds())
                game_time += time_diff

        return {"totalGame": game_number,
                "totalGameTime": game_time,
                "wonGame": game_won}
