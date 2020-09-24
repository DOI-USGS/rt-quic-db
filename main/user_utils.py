# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:25:20 2020

@author: NBOLLIG
"""
import random, string
import os
import smtplib


"""
Generate a plaintext password string
"""
def make_temp_password():
    length = 13
    chars = string.ascii_letters + string.digits + '!@#$%^&*()'
    random.seed = (os.urandom(1024))
    return ''.join(random.choice(chars) for i in range(length))

"""
Send a password reset email.
"""
def send_password_recovery_email(email, temp_password):
    gmail_user = os.getenv('GMAIL_USERNAME')
    gmail_password = os.getenv('GMAIL_PASSWORD')
    
    to = email
    subject = 'Your Quake password has been reset'
    body = 'Your Quake password has been reset. You will need to log in with the following temporary password:\r\n\r\n' + temp_password + '\r\n\r\nThis is an automated message.'
    
    email_text = """\
From: Quake Application
To: %s
Subject: %s

%s
""" % (to, subject, body)
    
    print(email_text)
    
    try:
        server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
        server.ehlo()
        server.login(gmail_user, gmail_password)
        server.sendmail(gmail_user, to, email_text)
        server.close()
        return True
    except:
        return False