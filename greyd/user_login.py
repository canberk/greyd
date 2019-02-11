# -*- coding: utf-8 -*-

"""
    User login service module.
    Greyd Rule: 4xx
"""

import sqlite3 as sql
import json
import logging
import requests
import config
from database import DatabaseGreyd


class UserLogin(DatabaseGreyd):
    """User create or login every android splash time."""

    def __init__(self):
        super(UserLogin, self).__init__()
        self.logger = logging.getLogger(__name__)

    def entry(self, greyd_rule, json_request):
        """Desicion is facebook login/create or guest create."""
        if greyd_rule == 401:
            response = self.__facebook_login__(json_request)
        elif greyd_rule == 402:
            response = self.__guest_login__(json_request)
        return response

    def __facebook_login__(self, json_request):
        """User Facebook Login Handler"""

        # TODO Android location error.
        facebook_id = json_request["facebookId"]
        full_name = json_request["fullName"]
        e_mail = json_request["eMail"]
        location = json_request["location"]
        city = self.__city_finder__(location)

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            user = cursor.execute("""SELECT * FROM user WHERE facebook_id=?""",
                                  (facebook_id,)).fetchone()

            # Is this user registered before on database?
            if not user:
                cursor.execute("""INSERT INTO user
                               (facebook_id, full_name, e_mail, location, 
                               location_city) VALUES (?,?,?,?,?)""",
                               (facebook_id, full_name, e_mail, location,
                                city,))
                database.commit()

                self.logger.info("Create new Facebook user facebookId:%s",
                                 facebook_id)
            else:
                cursor.execute("""
                UPDATE user SET location_city=? WHERE facebook_id=?""",
                               (city, facebook_id,))
                database.commit()

            user = cursor.execute("""SELECT * FROM user WHERE facebook_id=?""",
                                  (facebook_id,)).fetchone()

            greyd_id = user[0]
            user_status = user[4]

        response = {"success": True,
                    "greydRule": 401,
                    "greydId": greyd_id,
                    "userStatus": user_status}

        self.logger.info("New session for Facebook user facebookId: %s",
                         facebook_id)
        return response

    def __guest_login__(self, json_request):
        """Guest Login Handler"""
        # TODO Implement guest to greyd
        location = json_request["location"]
        with sql.connect(self.db_path) as database:
            cursor = database.cursor()

            cursor.execute("""INSERT INTO guest (location) VALUES (?)""",
                           (location,))
            database.commit()

            guest = cursor.execute("""SELECT max(guest_id) FROM guest""")\
                .fetchone()

            guest_id = guest[0]
        response = {"success": True,
                    "greydRule": 402,
                    'guestId': guest_id}

        self.logger.info("New guest guestId: %s", guest_id)

        return response

    def __city_finder__(self, location):
        """City finder with GEONAMES maps api."""

        latitude, longitude = location.split(",")
        result_city = ""
        geonames_url = f"http://api.geonames.org/findNearbyPlaceNameJSON?lat={latitude}&lng={longitude}&username={config.GEONAMES_USERNAME}"  # noqa pylint: disable=line-too-long

        for _ in range(5):
            request_map_api = requests.get(geonames_url)
            map_json_parse = json.loads(request_map_api.text)
            try:
                result_city = map_json_parse["geonames"][0]["adminName1"]
            except IndexError:
                result_city = ""

        return result_city
