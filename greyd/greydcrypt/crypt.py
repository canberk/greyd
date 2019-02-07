# -*- coding: utf-8 -*-

"""RSA encrypt decrypt."""

import base64
import random
import string
import rsa
from greydcrypt.aes_crypt import AESCipher


def decrypt(encrypted_text, local_private_rsa_key):
    """Decrypt the incoming request"""

    encrypted_text = base64.b64decode(encrypted_text)
    aes_key_in_rsa = encrypted_text[-64:]

    aes_key = rsa.decrypt(
        aes_key_in_rsa, rsa.PrivateKey(*local_private_rsa_key))
    aes_key = aes_key.decode('utf8')
    decoder = AESCipher(aes_key)

    clear_text = decoder.decrypt(encrypted_text[:-64])
    return clear_text


def encrypt(clear_text, global_public_rsa_key):
    """Encrypt the response"""

    aes_key = ''.join(
        random.choice(string.ascii_uppercase + string.digits) for _ in
        range(16))
    encoder = AESCipher(aes_key)
    cipher_text = encoder.encrypt(clear_text)
    aes_key = aes_key.encode("utf8")

    aes_key_in_rsa = rsa.encrypt(
        aes_key, rsa.PublicKey(*global_public_rsa_key))

    response_data = base64.b64encode(cipher_text + aes_key_in_rsa)
    return response_data
