# -*- coding: utf-8 -*-

"""
    File name: user_login.py
    Author: Canberk Özdemir
    Date created: 2/5/2018
    Date last modified: 1/21/2019
    Python version: 3.5.2

    User login service module.
    Greyd Rule: 4xx
"""

import sqlite3 as sql
import json
import logging
import requests
from database_connection import DatabeseGreyd


class UserLogin(DatabeseGreyd):
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

        # TODO(canberk) Android location error
        facebook_id = json_request["facebookId"]
        full_name = json_request["fullName"]
        e_mail = json_request["eMail"]
        location = json_request["location"]
        city = self.__city_finder__(location)

        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            user = cursor.execute("""
            SELECT * FROM user WHERE facebook_id=?""", (facebook_id,))\
                .fetchone()

            # Is this user registered before on database?
            if  not user:
                cursor.execute("""
                INSERT INTO user 
                    (facebook_id, 
                    full_name, 
                    e_mail,
                    location, 
                    location_city
                    ) 
                    VALUES (?,?,?,?,?)
                    """, (facebook_id, full_name, e_mail, location, city))
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
        response = {"success": True, "greydRule": 401, "greydId": greyd_id,
                    "userStatus": user_status}
        self.logger.info("New session for Facebook user facebookId: %s",
                         facebook_id)
        return response

    def __guest_login__(self, json_request):
        """Guest Login Handler"""
        location = json_request["location"]
        with sql.connect(self.db_path) as database:
            cursor = database.cursor()
            cursor.execute("""INSERT INTO guest (location) VALUES (?)""",
                           (location,))
            database.commit()
            guest = cursor.execute("""SELECT max(guest_id) FROM guest""")\
                .fetchone()

            guest_id = guest[0]
        response = {"success": True, "greydRule": 402, 'guestId': guest_id}
        self.logger.info("New guest guestId: %s", guest_id)
        return response

    def __city_finder__(self, location):
        """City finder with google maps api"""
        # TODO(canberk) Get better way for city finder.
        result_city = ""
        for i in range(5):
            request_map_api = requests.get(
                f"https://maps.googleapis.com/maps/api/geocode/json?latlng={location}&sensor=true&key=AIzaSyBkIAg4XR1OvXV8abfltn7krOACCLBDmoQ")
            map_json_parse = json.loads(request_map_api.text)
            try:
                for i in range(10):
                    result_level = map_json_parse["results"][0]["address_components"][i]["types"][0]
                    if result_level == "administrative_area_level_1":
                        result_city = map_json_parse["results"][0]["address_components"][i]["long_name"]
                        break
                if result_city != "":
                    break
            except IndexError:
                result_city = ""

        return result_city
