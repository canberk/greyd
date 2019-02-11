#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

"""
    Greyd starting script.
    Incoming Greyd request controller.
"""

import socket
import threading
import json
import logging.config
from statistics import UserStatistics
import config
from greydcrypt import crypt
from active_user import ActiveUser
from user_login import UserLogin
from lobby import LobbyTransaction


def setup_logging(path='logging.json'):
    """Setup logging configuration"""

    import os
    directory = "logfiles"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, 'rt') as file:
        log_config = json.load(file)
    logging.config.dictConfig(log_config)


def main_loop():
    """Socket connection main loop"""
    # pylint: disable=invalid-name

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config.HOST, config.PORT))
    LOGGER.info("Server is up")
    while 1:
        print("User waiting...")
        s.listen(5)
        connection, address = s.accept()
        LOGGER.info("One incoming connection: %s", address[0])
        data = connection.recv(4096).decode()
        if data == "CloseServer" and address[0] == config.HOST:
            s.close()
            LOGGER.info("Server closed normally.")
            break
        thread_controller = threading.Thread(
            target=main_controller(connection, data, address[0]))
        thread_controller.start()


def main_controller(connection, data, r_ip_address):
    """Main Controller function"""

    try:
        request = crypt.decrypt(data, config.SERVER_PRIVATE_RSA_KEY)
    except TypeError:
        # TODO Write decryption error handler.
        # TODO Crypt base64 Incorrect padding handler.
        response = 'password decryption error.'
        LOGGER.warning("Password decryption error. %s", r_ip_address)

    LOGGER.info("One request %s %s", request, r_ip_address)

    try:
        json_output = json.loads(request)
        is_success = json_output["success"]
    except (IndexError, ValueError, TypeError):
        # Incoming json data is not correct or not json.
        # TODO Write Response Json
        LOGGER.warning("Incoming json data is not correct or not json. %s",
                       r_ip_address)
        is_success = False

    if is_success:
        greyd_rule = json_output["greydRule"]
        greyd_rotation = greyd_rule // 100
        if greyd_rotation == 1:
            active_user = ActiveUser()
            response = active_user.entry(greyd_rule, json_output)
            del active_user
        elif greyd_rotation == 2:
            lobby = LobbyTransaction()
            response = lobby.entry(greyd_rule, json_output)
            del lobby
        elif greyd_rotation == 3:
            statistic = UserStatistics()
            response = statistic.entry(greyd_rule, json_output)
            del statistic
        elif greyd_rotation == 4:
            user_login = UserLogin()
            response = user_login.entry(greyd_rule, json_output)
            del user_login
        elif greyd_rotation == 5:
            # TODO Create class for server information monitored
            pass
        else:
            response = "Undefined greyd_rule request."
            LOGGER.error("Undefined greyd_rule request. %s", r_ip_address)
        response = json.dumps(response, sort_keys=True)

    else:
        # TODO Unsuccesful request handling
        response = "Unsuccessful request \n" + request + " X " + request
        LOGGER.warning("Unsuccessful request: " +
                       request + "Address:" + r_ip_address)

    LOGGER.info("Response: %s", response)
    response = crypt.encrypt(response, config.CLIENT_PUBLIC_RSA_KEY)
    connection.send(response)


if __name__ == "__main__":
    LOGGER = logging.getLogger(__name__)
    setup_logging()
    main_loop()
else:
    print("Greyd failure.")
