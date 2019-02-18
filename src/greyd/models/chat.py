# -*- coding: utf-8 -*-

"""chat table and chat model."""

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from greyd.db.base import Base
from greyd.models.user_to_lobby import UserToLobby

# pylint: disable=too-few-public-methods


class Chat(Base):
    """Chat object.
    This model add chat content and time for lobby on database.
    session_id tell which lobby and who owner of chat.

    session_id: user_to_lobby.id (ForeignKey)

    content: String (Not null)

    time: String (Default="01/01/1970 00:00")
        - mm/dd/yyyy HH:MM
    """
    __tablename__ = "chat"

    id = Column(Integer, primary_key=True)

    session_id = Column(Integer, ForeignKey("user_to_lobby.id"))
    session = relationship(UserToLobby, foreign_keys=[session_id])

    content = Column(String, nullable=False)
    time = Column(String, default="01/01/1970 00:00")
