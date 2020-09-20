# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:25:20 2020

@author: NBOLLIG
"""
import random, string
import os

"""
Generate a plaintext password string
"""
def make_temp_password():
    length = 13
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))