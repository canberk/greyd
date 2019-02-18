# -*- coding: utf-8 -*-

"""User login service module.
Greyd Rule: 4xx
"""

import logging

from greyd.db import session
from greyd.models.user import User


class UserLogin():
    """User create or login every android splash time."""
    logger = logging.getLogger(__name__)

    def __init__(self, request):
        self.request = request

    def entry(self):
        """Decide of the entry way. Response json.

        Greyd Rule  -   Entry Style
            401     -  Facebook
        """
        greyd_rule = self.request["greydRule"]
        if greyd_rule == 401:
            response = self._facebook_login()

        return response

    def _facebook_login(self):
        user = session.query(User).filter(
            User.facebook_id == self.request["facebookId"]).first()

        if not user:
            # If user does not exist.
            user = User(facebook_id=self.request["facebookId"],
                        full_name=self.request["fullName"],
                        e_mail=self.request["eMail"])
            session.add(user)
            session.commit()
            self.logger.info("New Facebook user GreydId: %s, FacebookId: %s",
                             user.id, user.facebook_id)

        # Update location information this login.
        user.location = self.request["location"]
        user.city_update()
        session.commit()

        self.logger.info("User logged in GreydId: %s", user.id)
        return {"success": True,
                "greydRule": self.request["greydRule"],
                "greydId": user.id,
                "userStatus": user.status}
