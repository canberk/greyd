#!/usr/bin/env/ python
# -*- coding: utf-8 -*-

import json
import socket
import config
from greydcrypt import crypt
from assertions import assert_valid_schema


def send_socket_request(request):
    """Send json request server and take response"""
    crypted = crypt.encrypt(request, config.SERVER_PUBLIC_RSA_KEY)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((config.HOST, config.PORT))   
    s.send(crypted)
    response = s.recv(1024)
    s.close()
    response = crypt.decrypt(response, config.CLIENT_PRIVATE_RSA_KEY)
    json_data = json.loads(response)
    return json_data

def test_facebook_user_login():
    """401 Facebook login or new Facebook create"""
    file = open("schemas/client-to-server/401-facebook-login.json")
    json_data = send_socket_request(file.read())
    assert_valid_schema(json_data, "schemas/server-to-client/401-facebook-login.json")

