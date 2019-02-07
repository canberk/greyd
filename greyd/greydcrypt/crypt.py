# -*- coding: utf-8 -*-

"""
    File name: crypt.py
    Author: Canberk Özdemir
    Date created: 2/5/2018
    Date last modified: 1/30/2019
    Python version: 3.7.2
"""

import base64
import random
import string
import rsa
from greydcrypt.aes_crypt import AESCipher


def decrypt(encrypted_text, LOCAL_PRIVATE_RSA_KEY):
    """Decrypt the incoming request"""
    encrypted_text = base64.b64decode(encrypted_text)
    aes_key_in_rsa = encrypted_text[-64:]
    aes_key = rsa.decrypt(
        aes_key_in_rsa, rsa.PrivateKey(*LOCAL_PRIVATE_RSA_KEY))
    aes_key = aes_key.decode('utf8')
    decoder = AESCipher(aes_key)
    clear_text = decoder.decrypt(encrypted_text[:-64])
    return clear_text


def encrypt(clear_text, GLOBAL_PUBLIC_RSA_KEY):
    """Encrypt the response"""
    aes_key = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in
        range(16))
    encoder = AESCipher(aes_key)
    cipher_text = encoder.encrypt(clear_text)
    aes_key = aes_key.encode("utf8")
    aes_key_in_rsa = rsa.encrypt(
        aes_key, rsa.PublicKey(*GLOBAL_PUBLIC_RSA_KEY))
    response_data = base64.b64encode(cipher_text + aes_key_in_rsa)
    return response_data
