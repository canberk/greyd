# -*- coding: utf-8 -*-

"""Set up environment configure."""

import os
import rsa
# pylint: disable=invalid-name

HOST = "10.20.30.10"
PORT = int(os.environ.get("PORT", "8001"))

KEYS_PATH = os.environ.get("KEYS_PATH", "/usr/src/app/rsa_keys/")


private_file = KEYS_PATH + "client_private.pem"
with open(private_file, mode="rb") as file:
    private_key_data = file.read()
CLIENT_PRIVATE_RSA_KEY = rsa.PrivateKey.load_pkcs1(private_key_data)

public_file = KEYS_PATH + "server_public.pem"
with open(public_file, mode="rb") as file:
    public_key_data = file.read()
SERVER_PUBLIC_RSA_KEY = rsa.PublicKey.load_pkcs1(public_key_data)
