# -*- coding: utf-8 -*-

"""user table and user model."""

from sqlalchemy import Column, Integer, String

from greyd.db.base import Base


class User(Base):
    """User object.

    facebook_id: Integer (Unique)

    full_name: String (Not null)

    e_mail: String

    status: Integer (Default=0)
        - 0 is regular
        - 1 is authorized
        - 2 is banned

    level: Integer (Default=1)

    total_score: Integer (Default=0)
        - Score is define to level. But didn't organized yet.

    location: String (Default="0.0,0.0")

    city: String
        - Location decide the city.
    """
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
    facebook_id = Column(String, unique=True)
    full_name = Column(String, nullable=False)
    e_mail = Column(String)
    status = Column(Integer, default=0)
    level = Column(Integer, default=1)
    total_score = Column(Integer, default=0)
    location = Column(String, default="0.0,0.0")
    city = Column(String)

    def city_update(self):
        """City updater for user"""
        self.city = self.city_finder(self.location.__str__())

    def add_point(self):
        """Add point for user."""
        self.total_score = self.total_score + 1
        if self.total_score // 10 == 0:
            self.level = self.total_score / 10

    @staticmethod
    def city_finder(location):
        """City update with GEONAMES maps api."""
        import requests
        import json
        from greyd import config
        latitude, longitude = location.split(",")
        result_city = ""
        geonames_url = f"http://api.geonames.org/findNearbyPlaceNameJSON?lat={latitude}&lng={longitude}&username={config.GEONAMES_USERNAME}"  # noqa pylint: disable=line-too-long

        for _ in range(5):
            request_map_api = requests.get(geonames_url)
            map_json_parse = json.loads(request_map_api.text)
            try:
                result_city = map_json_parse["geonames"][0]["adminName1"]
                break
            except IndexError:
                result_city = ""

        return result_city
