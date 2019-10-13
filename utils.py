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
        SELECT ID,PASSWORD,AUTH FROM USERS WHERE USERNAME = ?
    ''', (username,))
    user_id = None
    password_find = None
    auth_find = None
    try:
        for row in result:
            user_id = row[0]
            password_find = row[1]
            auth_find = row[2]
        if password_find == password:
            conn.close()
            return [user_id, auth_find]
    except IOError:
        conn.close()
        return None
    conn.close()
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


def verify_auth(auth, auth_need, params_need=None):
    return True


def verify_ip(token_ip, ip):
    if token_ip == ip:
        return True
    return False


def create_room(room_name, description, creator_id, auth_need):
    conn = None
    try:
        conn = sqlite3.connect("database/waitti_message.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO ROOMS (ROOM_NAME, DESCRIPTION, CREATOR_ID, AUTH_NEED)
            VALUES
            (?, ?, ?, ?)
        ''', (room_name, description, creator_id, auth_need))
        cursor.execute('''CREATE TABLE IF NOT EXISTS ''' + room_name.upper() +
                       ''' (
                       ID INTEGER PRIMARY KEY,
                       CONTENT TEXT NOT NULL,
                       SEND_DATE TEXT NOT NULL,
                       SEND_USER TEXT NOT NULL
                       );
                   ''')
        conn.commit()
        conn.close()
        return True
    except IOError:
        if conn is not None:
            conn.close()
        return False


def find_room_and_verify_auth(room_name, username, auth):
    conn = sqlite3.connect("database/waitti_message.db")
    cursor = conn.cursor()
    cursor.execute('''
        SELECT AUTH_NEED FROM ROOMS WHERE ROOM_NAME = ?
    ''', (room_name,))
    auth_find = None
    for row in cursor:
        auth_find = row[0]
    if auth_find is not None:
        if verify_auth(auth, auth_find):
            conn.close()
            return True
    conn.close()
    return False
