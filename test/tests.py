#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

"""Test Main"""

import json
import socket
import glob
import pytest
import config
from greydcrypt import crypt
from assertions import assert_valid_schema

SCHEMAS = [
    "401_facebook_login",
    "401_facebook_login_2",
    "402_guest_login",
    "201_create_lobby",
    "202_find_lobbies",
    "203_join_lobby",
    "102_refresh_lobby",
    "204_start_game",
    "101_refresh_user_in_game",
    "205_quit_lobby"
    # "302_get_statistics",
    # "301_get_score_info"
]


def send_socket_request(request):
    """Send json request server and take response."""
    # pylint: disable=invalid-name
    crypted = crypt.encrypt(request, config.SERVER_PUBLIC_RSA_KEY)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.HOST, config.PORT))
    s.send(crypted)
    response = s.recv(1024)
    s.close()
    response = crypt.decrypt(response, config.CLIENT_PRIVATE_RSA_KEY)
    json_data = json.loads(response)
    return json_data


@pytest.mark.parametrize("schema", SCHEMAS)
def test_schemas(schema):
    """Test all schemas."""

    file = open("schemas/client-to-server/" + schema + ".json")
    json_data = send_socket_request(file.read())
    greyd_rule = schema[:3]
    assert_file = glob.glob("schemas/server-to-client/"
                            + greyd_rule + "*")
    assert_valid_schema(json_data, assert_file[0])
