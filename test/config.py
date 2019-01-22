# -*- coding: utf-8 -*-

import os

HOST = "10.20.30.10"
PORT = int(os.environ["PORT"])
CLIENT_PRIVATE_RSA_KEY = tuple(map(int, os.environ["CLIENT_PRIVATE_RSA"].split(",")))
SERVER_PUBLIC_RSA_KEY = tuple(map(int, os.environ["SERVER_PUBLIC_RSA"].split(",")))
