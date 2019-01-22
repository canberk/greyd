# -*- coding: utf-8 -*-

import os

HOST = os.environ["HOST"]
PORT = int(os.environ["PORT"])

DB_NAME = "greyd.db"
DB_PATH = "/db"

SERVER_PRIVATE_RSA_KEY = tuple(map(int, os.environ["SERVER_PRIVATE_RSA"].split(",")))
CLIENT_PUBLIC_RSA_KEY = tuple(map(int, os.environ["CLIENT_PUBLIC_RSA"].split(",")))
