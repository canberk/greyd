# -*- coding: utf-8 -*-

"""Lobby table and lobby model."""

from datetime import datetime
from geopy.distance import great_circle
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from greyd.db.base import Base
from greyd.models.user import User


class Lobby(Base):
    """Lobby object.

    creator_id: user.id (ForeignKey)
        - Who create and owner this lobby.

    status: Integer (Default=0)
        - 0  Preparing.
        - 1  On game.
        - 2  Finished.

    center_location: String (Default="0.0,0.0")
        - Lobby creator first location.

    name: String (Not null)
        - Lobby name.

    game_distance: Integer (Default=25)
        - Define game circle.
        - Type is m^2

    setup_time: String
        - mm/dd/yyyy HH:MM
        - Lobby ceration time.

    start_time: String
        - mm/dd/yyyy HH:MM
        - Game start time.

    end_time: String
        - mm/dd/yyyy HH:MM
        - Lobby and game end time.

    life_number: Integer (Default=0)
        - Describe of user starts life.
        - If 0 than game will be end with time.

    max_time: Integer (Default=0)
        - Describe how long it will take this game.

    current_bait_location: String
        - Type like "0.0,0.0"

    winner_id: user.id (ForeignKey)
        - Who won that game.
    """
    __tablename__ = "lobby"

    id = Column(Integer, primary_key=True)

    creator_id = Column(Integer, ForeignKey("user.id"))
    creator_user = relationship(User, foreign_keys=[creator_id])

    status = Column(Integer, default=0)
    center_location = Column(String, default="0.0,0.0")
    name = Column(String, nullable=False)
    game_distance = Column(Integer, default=25)
    setup_time = Column(String)
    start_time = Column(String)
    end_time = Column(String)
    life_number = Column(Integer, default=0)
    max_time = Column(Integer, default=0)
    bait_location = Column(String)

    winner_id = Column(Integer, ForeignKey("user.id"))
    winner_user = relationship(User, foreign_keys=[winner_id])

    time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.now())

    def start_game(self):
        """Start game initialize configurations."""
        # Status: On game
        self.status = 1
        self.start_time = self.time_now
        self.new_bait()

    def end_game(self):
        """Lobby owner has quit or game is end regular."""
        # Status : End Game
        self.status = 2
        self.end_time = self.time_now

    def new_bait(self):
        """New bait location for lobby."""
        import random
        longitude, latitude = self.center_location.__str__().split(",")
        new_longitude = longitude[:-3] + str(random.randint(100, 999))
        new_latitude = latitude[:-3] + str(random.randint(100, 999))
        self.bait_location = new_longitude + "," + new_latitude

    def is_bait_taken(self, user_location):
        """Calculate distance from user and bait."""
        circle = great_circle(user_location, self.bait_location).km
        if circle < 0.01:
            self.new_bait()
            return True
        return False
