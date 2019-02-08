# -*- coding: utf-8 -*-

"""Set up environment configure."""

import os
import rsa
# pylint: disable=invalid-name


def use_rsa_key(keys_path):
    """Check if already have keypair do nothing else create new one."""
    if not check_pem_files(keys_path):
        generate_rsa_keypair(keys_path)


def check_pem_files(keys_path):
    """Check *_public.pem and *_private.pem is exist."""
    from pathlib import Path
    pub_file = Path(keys_path + "_public.pem")
    pri_file = Path(keys_path + "_private.pem")
    return bool(pub_file.is_file() and pri_file.is_file())


def generate_rsa_keypair(keys_path):
    """Generate rsa keypair."""
    (public_key, private_key) = rsa.newkeys(512)

    if not os.path.exists(keys_path):
        os.makedirs(keys_path)
    with open(keys_path + "_public.pem", "wb+") as file:  # noqa pylint: disable=redefined-outer-name
        key_data = rsa.PublicKey.save_pkcs1(public_key)
        file.write(key_data)

    with open(keys_path + "_private.pem", "wb+") as file:
        key_data = rsa.PrivateKey.save_pkcs1(private_key)
        file.write(key_data)


SERVER_NAME = "server"
CLIENT_NAME = "client"

HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])

DB_NAME = "greyd.db"
DB_PATH = "/db"

GEONAMES_USERNAME = os.environ["GEONAMES_USERNAME"]

KEYS_PATH = "/usr/src/app/rsa_keys/"

use_rsa_key(KEYS_PATH + SERVER_NAME)
use_rsa_key(KEYS_PATH + CLIENT_NAME)

private_file = KEYS_PATH + SERVER_NAME + "_private.pem"
with open(private_file, mode="rb") as file:
    private_key_data = file.read()
SERVER_PRIVATE_RSA_KEY = rsa.PrivateKey.load_pkcs1(private_key_data)

public_file = KEYS_PATH + CLIENT_NAME + "_public.pem"
with open(public_file, mode="rb") as file:
    public_key_data = file.read()
CLIENT_PUBLIC_RSA_KEY = rsa.PublicKey.load_pkcs1(public_key_data)
