# -*- coding: utf-8 -*-

"""user_location table and model."""

from sqlalchemy import Column, ForeignKey, Integer, String, Boolean
from sqlalchemy.orm import relationship

from greyd.db.base import Base
from greyd.models.user_to_lobby import UserToLobby


class UserLocation(Base):
    """UserLocation object. Save users footprint in game.

    session_id: user_to_lobby.id (ForeignKey)

    location: String (Default="0.0,0.0)

    time: String (Default="01/01/1970 00:00")
        - mm/dd/yyyy HH:MM

    bait_location: String (Default="0.0,0.0")

    is_bait_taken: Boolean (Default=False)
        - Bait is taken or not.
    """
    __tablename__ = "user_location"

    id = Column(Integer, primary_key=True)

    session_id = Column(Integer, ForeignKey("user_to_lobby.id"))
    session = relationship(UserToLobby, foreign_keys=[session_id])

    location = Column(String, default="0.0,0.0")
    time = Column(String, default="01/01/1970 00:00")
    bait_location = Column(String, default="0.0,0.0")
    is_bait_taken = Column(Boolean, nullable=False)
