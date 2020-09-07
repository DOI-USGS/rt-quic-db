# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:25:20 2020

@author: NBOLLIG
"""
import random, string
from passlib.hash import sha512_crypt

"""
Generate a password hash using SHA-512 with a provided salt.
"""
def make_hash(password, salt):
    return sha512_crypt.using(salt=salt).hash(password)

"""
Used during password creation to create dynamic salt.
"""
def generate_salt(k=16):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=k))