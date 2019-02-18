#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

"""Greyd main entry point.
Incoming Greyd request controller.
"""

import socket
import threading
import json
import logging.config

from greyd import config
from greyd.greyd_crypt import crypt
from greyd.active_user import ActiveUser
from greyd.lobby_transaction import LobbyTransaction
from greyd.statistics import UserStatistics
from greyd.user_login import UserLogin

LOGGER = logging.getLogger(__name__)


def setup_logging(path='greyd/logging.json'):
    """Setup logging configuration."""
    import os
    directory = "logfiles"
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(path, 'rt') as file:
        log_config = json.load(file)
    logging.config.dictConfig(log_config)


def main_loop():
    """Tcp socket connection from client."""
    # pylint: disable=invalid-name
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((config.HOST, config.PORT))
    LOGGER.info("Server is up on port %s", config.PORT)

    while True:
        s.listen(5)
        connection, address = s.accept()
        data = connection.recv(4096).decode()
        thread_controller = threading.Thread(
            target=main_controller(connection, data, address[0]))
        thread_controller.start()


def json_check(request, ip_address):
    """Data is json or not."""
    try:
        json_output = json.loads(request)
        return json_output, True
    except (IndexError, ValueError, TypeError):
        error_msg = "Request json data is not correct or not json."
        LOGGER.error("%s Ip Address: %s", error_msg, ip_address)
        response = {"success": False,
                    "errorType": error_msg}
        return json_output, response


def decrypt_check(crypted, ip_address):
    """Decrypt request with greyd_decyrpt."""
    try:
        request = crypt.decrypt(crypted, config.SERVER_PRIVATE_RSA_KEY)
        request, response = json_check(request, ip_address)
    except TypeError:
        error_msg = "Password decryption error."
        LOGGER.error("%s Ip address:%s", error_msg, ip_address)
        response = {"success": False,
                    "errorType": error_msg}
    return request, response


def main_controller(connection, data, request_ip_addr):
    """Main controller
    Decrypt request and then decide rotation for greyd rule.
    """
    request, response = decrypt_check(data, request_ip_addr)

    if request["success"]:
        # Find greyd rule
        rotation = request["greydRule"] // 100

        if rotation == 1:
            response = ActiveUser(request).entry()
        elif rotation == 2:
            response = LobbyTransaction(request).entry()
        elif rotation == 3:
            response = UserStatistics(request).entry()
        elif rotation == 4:
            response = UserLogin(request).entry()
        else:
            error_msg = "Undefined Greyd Rule request."
            response = {"success": False,
                        "errorType": error_msg}
            LOGGER.error("%s Ip address:%s", error_msg, request_ip_addr)

    elif not request["success"]:
        error_msg = "Unsuccessful request."
        response = {"success": False,
                    "errorType": error_msg}
        LOGGER.error("%s : %s  Ip Address:%s",
                     error_msg, request, request_ip_addr)

    response = json.dumps(response, sort_keys=True)
    # LOGGER.info("Response: %s", response)
    response = crypt.encrypt(response, config.CLIENT_PUBLIC_RSA_KEY)
    connection.send(response)


if __name__ == "__main__":
    setup_logging()
    main_loop()
