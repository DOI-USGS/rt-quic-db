# -*- coding: utf-8 -*-
"""
Created on Sun Sep  6 18:25:20 2020

@author: NBOLLIG
"""
import random, string
import os
import smtplib
from werkzeug.routing import RequestRedirect

import model

START_ADMIN_SEC_PTS = 500

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
    except Exception as e:
        print(e)
        return False

"""
Check the session cookie for a security point
"""
def has_security_point(session, sec_point, refresh=True):
    if refresh:
        refresh_user_security(session)
    security_points = session['security_points']
    if session['activated'] == 1 and sec_point in security_points:
        return True
    elif session['activated'] != 1:
        raise RequestRedirect('/index')
    else:
        return False

"""
Update the activation status and security points for the user_id cached in the session cookie.
"""
def refresh_user_security(session):
    user_ID = session['user_ID']
    userModel = model.ManageUser()
    session['activated'] = userModel.get_activation_status(user_ID)
    session['security_points'] = userModel.get_security_points(user_ID)
