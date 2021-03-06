from flask import session
import base64

from database.db_answer import DBAnswer, DBError, OK
from database.db_table import DBTable
from database.common_functions import *


class User:
    def __init__(self, ID, username, password_hash, avatar):
        self.id = ID
        self.username = username
        self.password_hash = password_hash
        self.avatar = avatar

    def __str__(self):
        return 'id: {}; username: {}; password_hash: {};'.format(
               self.id, self.username, self.password_hash)


class UsersTable(DBTable):

    def get_by_name(self, username):
        data = self.execute('SELECT * FROM users WHERE username=?', [username])
        user_data = data.fetchone()
        if user_data is None:
            return None
        return User(*user_data)

    def get_by_id(self, ID):
        data = self.execute('SELECT * FROM users WHERE id=?', [ID])
        user_data = data.fetchone()
        if user_data is None:
            return None
        return User(*user_data)

    def current_username(self):
        return session.get('username')

    def current(self):
        return self.get_by_name(self.current_username())

    def have_user(self, username):
        return not self.get_by_name(username) is None

    def number_of_users(self):
        data = self.execute('SELECT id FROM users')
        return len(data.fetchall())

    def add(self, username, password):
        if self.have_user(username):
            return DBAnswer(False, DBError.IncorrectUsername,
                            'User with same username already exist')
        if False:  # TODO check username for length and invalid characters
            return DBAnswer(False, DBError.IncorrectUsername,
                            'Username contains invalid characters or too short/long')
        if False:  # TODO check password for length and invalid characters
            return DBAnswer(False, DBError.IncorrectPassword,
                            'Password contains invalid characters or too short')

        password_hash = sha1_hash(password)
        ID = self.number_of_users()
        avatar = 'default.png'

        self.execute('''INSERT INTO users (id, username, password_hash, avatar)
                               VALUES (?, ?, ?, ?) ''', [ID, username, password_hash, avatar])
        return DBAnswer(True, OK, 'User successfully created')

    # password

    def set_password(self, password, username=None):
        if username is None:
            return self.set_password(password, username=self.current_username())
            
        if False:  # TODO check password for length and invalid characters
            return DBAnswer(False, DBError.IncorrectPassword,
                            'Password contains invalid characters or too short')

        if not self.have_user(username):
            return DBAnswer(False, DBError.IncorrectUser,
                            'Can\'t set password for nonexistent user.')

        password_hash = sha1_hash(password)
        self.execute('''UPDATE users SET password_hash=? WHERE username=?''',
                     [password_hash, username])
        return DBAnswer(True, OK, 'Password successfully changed')

    def check_password(self, password, username=None):
        if username is None:
            return self.check_password(password, self.current_username())

        if not self.have_user(username):
            return False

        return self.get_by_name(username).password_hash == sha1_hash(password)

    # username

    def set_username(self, new_username, username=None):
        if username is None:
            return self.set_username(new_username, self.current_username())

        if self.have_user(new_username):
            return DBAnswer(False, DBError.IncorrectUsername,
                            'User with same username already exist')
        if False:  # TODO check username for length and invalid characters
            return DBAnswer(False, DBError.IncorrectUsername,
                            'Username contains invalid characters or too short/long')
        if not self.have_user(username):
            return DBAnswer(False, DBError.IncorrectUser,
                            'Can\'t set username for nonexistent user.')

        self.execute('''UPDATE users SET username=? WHERE username=?''',
                     [new_username, username])
        return DBAnswer(True, OK, 'Username successfully changed')

    # avatar

    def set_avatar(self, avatar_b64, username=None):
        if username is None:
            return self.set_avatar(avatar_b64, self.current_username())

        if not self.have_user(username):
            return DBAnswer(False, DBError.IncorrectUser,
                            'Can\'t set avatar for nonexistent user.')

        startstring = 'data:image/png;base64,'
        path = 'app/static/images/avatars/'

        if not avatar_b64.startswith(startstring):
            return DBAnswer(False, DBError.IncorrectAvatar,
                            'Avatar string must be started with "' + startstring + '"')
        try:
            avatar = base64.decodebytes(avatar_b64[len(startstring):].encode('utf-8'))
        except:
            return DBAnswer(False, DBError.IncorrectAvatar,
                            'Can\'t decode avatar. It must be encoded with base64 format')

        filename = gen_file_name(path, 10) + '.png'
        if not self.get_by_name(username).avatar == 'default.png':
            os.remove(path + self.get_by_name(username).avatar)
        with open(path + filename, 'wb') as f:
            f.write(avatar)

        self.execute('UPDATE users SET avatar=? WHERE username=?', (filename, username))

        return DBAnswer(True, OK, 'Avatar successfully changed')

    def get_avatar(self, username=None):
        if username is None:
            return self.get_avatar(self.current_username())

        if not self.have_user(username):
            return None

        return self.get_by_name(username).avatar
