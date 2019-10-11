import jwt
from flask import current_app
import datetime
import sqlite3
import hashlib


def generate_jwt(payload, expiry, secret=None):
    """
    生成jwt
    :param payload: dict 载荷
    :param expiry: datetime 有效期
    :param secret: 密钥
    :return: jwt
    """
    _payload = {'exp': expiry, 'iat': datetime.datetime.utcnow()}
    _payload.update(payload)

    if not secret:
        secret = current_app.config['JWT_SECRET']

    token = jwt.encode(_payload, secret, algorithm='HS256')
    return token


def verify_jwt(token, secret=None):
    """
    检验jwt
    :param token: jwt
    :param secret: 密钥
    :return: dict: payload
    """
    if not secret:
        secret = current_app.config['JWT_SECRET']

    try:
        payload = jwt.decode(token, secret, algorithm=['HS256'])
    except jwt.PyJWTError:
        payload = None

    return payload


def verify_user(username, password):
    conn = sqlite3.connect("database/waitti_message.db")
    cursor = conn.cursor()
    result = cursor.execute('''
        SELECT ID,PASSWORD FROM USERS WHERE USERNAME = ?
    ''', (username, ))
    user_id = None
    password_find = None
    try:
        for row in result:
            user_id = row[0]
            password_find = row[1]
        if password_find == password:
            return user_id
    except IOError:
        return None
    return None


def add_user(username, nickname, password, mailbox):
    conn = sqlite3.connect("database/waitti_message.db")
    cursor = conn.cursor()
    if verify_user(username, password) is None:
        cursor.execute('''
            INSERT INTO USERS (USERNAME, NICKNAME, PASSWORD, MAILBOX, AUTH)
            VALUES (?, ?, ?, ?, ?)
        ''', [username, nickname, password, mailbox, "USER"])
        conn.commit()
        conn.close()
        return True
    else:
        conn.close()
        return False


def pass_to_md5(password):
    return hashlib.md5(password.encode(encoding='UTF-8')).hexdigest()