import datetime
import json
import logging
import smtplib
import ssl
import threading
import time
from email.message import EmailMessage
from itsdangerous import URLSafeTimedSerializer
from pip import main
import jwt
import re
#from flask.ext.mail import Message

from marshmallow import fields, Schema

import re
TAG_RE = re.compile(r'<[^>]+>')    
from contextlib import contextmanager
from mongoengine import connect, disconnect

#from Settings.config import DevelopmentConfig

from werkzeug.utils import secure_filename

from werkzeug.datastructures import FileStorage

from fileinput import filename
import os


ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg", "gif","svg"]


def GenerateApiToken():
    return("1234567890")

def email_notification(report,email):
    try:
        msg = EmailMessage()
        msg.set_content(json.dumps(report))
        msg["Subject"] = " Reset Password "
        msg["From"] = "xlrt.prod.news@gmail.com"
        msg["To"] = str(email)
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
            smtp.starttls(context=context)
            smtp.login(msg["From"], "ymzs epbb hbqk sxij")
            smtp.send_message(msg)
        response = {"status": 'success', "message": 'message sent through email'}
        return response
    except Exception as e:
        response = {"status": 'error', "message": f'{str(e)}'}
        return response


def event(event_name):
    def decorator(method):
        def timer(*args, **kwargs):
            _event_name = event_name.replace(" ", "_")
            logger = logging.getLogger(_event_name)
            ex = None
            data = None
            result = "SUCCESS"
            begin = time.time()
            try:
                data = method(*args, **kwargs)
            except Exception as e:
                ex = e
                result = "FAILURE"
            end = time.time()
            response = json.dumps(
                {
                    "eventName": _event_name,
                    "status": result,
                    "eventTime": end - begin,
                    "metaData": {
                        "thread": threading.current_thread().ident,
                        "class": method.__class__.__name__,
                        "method": method.__name__,
                    },
                },
            )
            if ex:
                logger.error(response)
                raise ex
            logger.info(response)
            return data

        return timer

    return decorator


def generate_token_reset_password(client_id):
    try:
        payload = {
                    'id': client_id,  
                    'exp': datetime.datetime.utcnow() + datetime.timedelta(days=5),
                }
                
        jwt_token = jwt.encode(payload, "SECRET", algorithm='HS256')
        
        return jwt_token
    except Exception as e:
        response = {"status": 'error', "message": f'{str(e)}'}
        return response


def verify_reset_token(headers):
                                
        try:
            
            decoded_token = jwt.decode(headers, 'SECRET', algorithms=['HS256'])
            
            
            response = {"status": 'True', "message": decoded_token.get("id")}
            return response 
            
        except jwt.ExpiredSignatureError as e:
            response = {"status": 'error', "message": f'{str(e)}'}
            return response 

@contextmanager
def connect_to_db():
    disconnect()
    connection = connect(
        host = "mongodb://localhost:27017/MYPAFWAY"
    )
    yield connection
    disconnect()

def save_image(image:FileStorage, folder:str=None)->str:

    if image and  image.filename.split(".")[-1].lower() in ALLOWED_EXTENSIONS:
            filename = secure_filename(image.filename)
            image.save(os.path.join("uploads/"+folder, filename))
            return "uploads/"+folder +filename

def email_notification_for_contact_user(report,subject,email):
    try:
        msg = EmailMessage()
        msg.set_content(report)
        msg["Subject"] = subject
        msg["From"] = "mypafway@dev13.ivantechnology.in"
        msg["To"] = str(email)
        context = ssl.create_default_context()
        with smtplib.SMTP("mail.dev13.ivantechnology.in", port=465) as smtp:
            smtp.starttls(context=context)
            smtp.login(msg["From"], "ECpNz3HtlcXN")
            smtp.send_message(msg)
        response = {"status": 'success', "message": 'message sent through email'}
        return response
    except Exception as e:
        response = {"status": 'error', "message": f'{str(e)}'}
        return response

def email_notification_for_setting_user(report,email):
    try:
        msg = EmailMessage()
        msg.set_content(report)
        msg["Subject"] = "Email to setting user "
        msg["From"] = "xlrt.prod.news@gmail.com"
        msg["To"] = email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
            smtp.starttls(context=context)
            smtp.login(msg["From"], "ymzs epbb hbqk sxij")
            smtp.send_message(msg)
        response = {"status": 'success', "message": 'message sent through email'}
        return response
    except Exception as e:
        response = {"status": 'error', "message": f'{str(e)}'}
        return response

def remove_tags(text):
    return TAG_RE.sub('', text)

def email_notification_for_user(report,email):
    try:
        msg = EmailMessage()
        msg.set_content(json.dumps(report))
        msg["Subject"] = " "
        msg["From"] = "xlrt.prod.news@gmail.com"
        msg["To"] = email
        context = ssl.create_default_context()
        with smtplib.SMTP("smtp.gmail.com", port=587) as smtp:
            smtp.starttls(context=context)
            smtp.login(msg["From"], "ymzs epbb hbqk sxij")
            smtp.send_message(msg)
        response = {"status": 'success', "message": 'message sent through email'}
        return response
    except Exception as e:
        response = {"status": 'error', "message": f'{str(e)}'}
        return response


# def generate_confirmation_token(email):
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     return serializer.dumps(email, salt=app.config['SECURITY_PASSWORD_SALT'])


# def confirm_token(token, expiration=3600):
#     serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
#     try:
#         email = serializer.loads(
#             token,
#             salt=app.config['SECURITY_PASSWORD_SALT'],
#             max_age=expiration
#         )
#     except:
#         return False
#     return email





# def send_email(to, subject, template):
#     msg = Message(
#         subject,
#         recipients=[to],
#         html=template,
#         sender=app.config['MAIL_DEFAULT_SENDER']
#     )
#     mail.send(msg)