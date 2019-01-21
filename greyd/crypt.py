"""
    File name: crypt.py
    Author: Canberk Özdemir
    Date created: 2/5/2018
    Date last modified: 1/21/2019
    Python version: 3.5.2

    This module decrypt the android client request and encrypt the response
"""

import os
import base64
import random
import string
import rsa
from aes_crypt import AESCipher

__SERVER_PRIVATE_RSA_KEY = os.environ["SERVER_PRIVATE_RSA"]
__CLIENT_PUBLIC_RSA_KEY = os.environ["CLIENT_PUBLIC_RSA"]

def decrypt(encrypted_text):
    """Decrypt the incoming request"""
    encrypted_text = base64.b64decode(encrypted_text)
    aes_key_in_rsa = encrypted_text[-64:]
    aes_key = rsa.decrypt(aes_key_in_rsa, __SERVER_PRIVATE_RSA_KEY)
    aes_key = aes_key.decode('utf8')
    decoder = AESCipher(aes_key)
    clear_text = decoder.decrypt(encrypted_text[:-64])
    return clear_text


def encrypt(clear_text):
    """Encrypt the response"""
    aes_key = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in
        range(16))
    encoder = AESCipher(aes_key)
    cipher_text = encoder.encrypt(clear_text)
    aes_key = aes_key.encode("utf8")
    aes_key_in_rsa = rsa.encrypt(aes_key, __CLIENT_PUBLIC_RSA_KEY)
    response_data = base64.b64encode(cipher_text + aes_key_in_rsa)
    return response_data
