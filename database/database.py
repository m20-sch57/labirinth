from flask import session
import sqlite3


def connection():
    connect = sqlite3.connect('database.db', check_same_thread = False)
    cursor = connect.cursor
    return connect, cursor

def init_db():
    connect, cursor = connection()

    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                      id TEXT PRIMARY KEY,
                      username TEXT, 
                      password_hash TEXT,
                      avatar TEXT
                      )''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS rooms (
                      id TEXT PRIMARY KEY,
                      name TEXT,
                      creator TEXT,
                      description TEXT, 
                      users TEXT,
                      create_date TEXT,
                      FOREIGN KEY (creator) REFERENCES users (username)
                      )''')

def drop_db():
    connect, cursor = connection()

    cursor.execute('DROP TABLE rooms')
    cursor.execute('DROP TABLE users')
    connect.commit()


class Database:
    def __init__(self):
        init_db()
        self.users = UsersTable(self)
        self.rooms = RoomsTable(self)
