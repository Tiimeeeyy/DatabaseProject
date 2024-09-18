# Script to encrypt sensitive information like passwords

import base64

from Crypto.Cipher import AES


def encrypt(data, key):
    cipher = AES.new(key, data)
    nonce = cipher.nonce
    ciphertext, tag = cipher.encrypt_and_digest(data.encode('utf-8'))
    return base64.b64encode(nonce + ciphertext).decode('utf-8')


def decrypt(encrypted_data, key):
    encrypted_data = base64.b64decode(encrypted_data)
    nonce = encrypted_data[:16]
    ciphertext = encrypted_data[16:]
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    return cipher.decrypt(ciphertext).decode('utf-8')
