import sqlite3


def database_connect():
    conn = sqlite3.connect("database/waitti_message.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS USERS
        (
        ID INTEGER PRIMARY KEY,
        USERNAME TEXT NOT NULL,
        NICKNAME TEXT NOT NULL,
        PASSWORD TEXT NOT NULL,
        MAILBOX TEXT NOT NULL,
        AUTH TEXT NOT NULL,
        AVATAR TEXT
        );
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ROOMS
        (
        ID INTEGER PRIMARY KEY,
        ROOM_NAME TEXT NOT NULL,
        DESCRIPTION TEXT NOT NULL,
        CREATOR_ID TEXT NOT NULL,
        AUTH_NEED TEXT NOT NULL
        );
    ''')
    conn.commit()
    conn.close()
