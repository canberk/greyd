#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

"""
    File name: main.py
    Author: Canberk Özdemir
    Date created: 9/29/2017
    Date last modified: 1/21/2019
    Python version: 3.5.2

    Greyd starting script.
    Incoming Greyd request controller.
"""

import os
import socket
import threading
import crypt
import json
import logging.config
from statistics import UserStatistics
from active_user import ActiveUser
from user_login import UserLogin
from lobby import LobbyTransaction

HOST = "0.0.0.0"
PORT = 8001
LOGGER = logging.getLogger(__name__)


def main_loop():
    """Socket programming main loop"""
    soket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    soket.bind((HOST, PORT))
    LOGGER.info("Server is up")
    while 1:
        print("User waiting...")
        soket.listen(5)
        connection, address = soket.accept()
        LOGGER.info("One incoming connection: %s", address[0])
        data = connection.recv(1024).decode()
        # print("Cipher data: " + data)
        if data == "CloseServer" and address[0] == HOST:
            soket.close()
            LOGGER.info("Server closed normally.")
            break
        thread_controller = threading.Thread(
            target=main_controller(connection, data, address[0]))
        thread_controller.start()


def main_controller(connection, data, r_ip_address):
    """Main Controller method"""

    try:
        request = crypt.decrypt(data)
    except TypeError:
        # TODO(canberk) Write decryption error handling. Crypt base64 Incorrect padding handling
        response = 'password decryption error.'
        LOGGER.warning("Password decryption error. %s", r_ip_address)

    LOGGER.info("One request %s %s", request, r_ip_address)

    try:
        json_output = json.loads(request)
        is_success = json_output["success"]
    except (IndexError, ValueError, TypeError):
        # Incoming json data is not correct or not json.
        # TODO(canberk) Write Response Json
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
            # TODO(canberk) Create class for server information monitored
            pass
        else:
            response = "Undefined greyd_rule request"
            LOGGER.error("Undefined greyd_rule request. %s", r_ip_address)
        response = json.dumps(response, sort_keys=True)
    else:
        # TODO(canberk) Unsuccesful request handling
        response = "Unsuccessful request \n" + request + " X " + request
        LOGGER.warning(
            "Unsuccessful request: " + request + "Address:" + r_ip_address)

    print("Response: " + response)
    response = crypt.encrypt(response)
    connection.send(response)


def setup_logging(
        default_path='logging.json', default_level=logging.INFO,
        env_key='LOG_CFG'):
    """Setup logging configuration"""
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as file:
            config = json.load(file)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)


if __name__ == "__main__":
    setup_logging()
    main_loop()
else:
    print("Greyd failure.")
