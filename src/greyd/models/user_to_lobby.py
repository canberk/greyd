# -*- coding: utf-8 -*-

"""User's lobby information model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from greyd.db.base import Base
from greyd.models.user import User
from greyd.models.lobby import Lobby

# pylint: disable=too-few-public-methods


class UserToLobby(Base):
    """Lobbies user information.(Session)

    lobby_id: lobby.id (ForeignKey)
    user_id: user.id (ForeignKey)
    entry_time: String (mm/dd/yyyy HH:mm)
        - entry_time said user when entry that lobby.

    exit_time: String (mm/dd/yyyy HH:mm)
        - User can be exit before the game does not finish.
        - Either ways exit time must be added here.

    remaining_life: Integer (Default=0)
        - If remaining life is 0 user is lose or game type is different to life
        ending.

    collected_bait Integer (Default=0)
        - User total collected bait in this lobby.

    is_game_won: Boolean
        - If game is end and user still part of lobby. User has win or not.
    """
    __tablename__ = "user_to_lobby"

    id = Column(Integer, primary_key=True)

    lobby_id = Column(Integer, ForeignKey("lobby.id"))
    lobby = relationship(Lobby, foreign_keys=[lobby_id])

    user_id = Column(Integer, ForeignKey("user.id"))
    user = relationship(User, foreign_keys=[user_id])

    entry_time = Column(String, default="01/01/1970 00:00")
    exit_time = Column(String, default="01/01/1970 00:00")

    remaining_life = Column(Integer, default=0)
    collected_bait = Column(Integer, default=0)
    is_game_won = Column(Boolean)
