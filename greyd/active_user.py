# -*- coding: utf-8 -*-

"""
    File name: active_user.py
    Author: Canberk Özdemir
    Date created: 5/23/2018
    Date last modified: 1/22/2019
    Python version: 3.5.2

    Active user in game
    Greyd Rule: 1xx
"""

import datetime
import logging
from database import DatabaseGreyd


class ActiveUser(DatabaseGreyd):
    """Active game greyd rules handler"""

    def __init__(self):
        super(ActiveUser, self).__init__()
        self.logger = logging.getLogger(__name__)
        self.time_now = '{0:%m/%d/%Y %H:%M}'.format(datetime.datetime.now())

    def entry(self, greyd_rule, json_request):
        """Desicion of request rotation for active user request"""
        if greyd_rule == 101:
            response = self.__game_active_user__(json_request)
        elif greyd_rule == 102:
            response = self.__refresh_lobby__(json_request)
        return response

    def __game_active_user__(self, json_request):
        """Return other lobby friends information in game"""
        # TODO(canberk) Game Active User absolutely empty
        pass

    def __refresh_lobby__(self, json_request):
        """Return other lobby friends information in lobby"""
        # TODO(canberk) Refresh lobby
        pass
