# -*- coding: utf-8 -*-

"""
    User statistics module.
    Greyd Rule: 3xx
"""
import logging
from database import DatabaseGreyd


class UserStatistics(DatabaseGreyd):
    """User statistics information."""

    def __init__(self):
        super(UserStatistics, self).__init__()
        self.logger = logging.getLogger(__name__)

    def entry(self, greyd_rule, json_request):
        """Desicion statistic/score information"""
        if greyd_rule == 301:
            response = self.__get_score__(json_request)
        elif greyd_rule == 302:
            response = self.__get_statistics__(json_request)
        return response

    def __get_score__(self, json_request):
        """Return score information."""
        pass

    def __get_statistics__(self, json_request):
        """Return statistics information to world,friends,city"""
        pass
