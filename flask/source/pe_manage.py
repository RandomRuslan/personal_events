class Manager:

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_user(self, email, password):
        try:
            self.db_conn.store_user(email, password)
        except:
            return False

        return True

    def check_user_error(self, email, hash_password):
        user = self.db_conn.load_user(email)
        if not user:
            return 'User does not exist'

        if hash_password != user['password']:
            return 'Incorrect email/password'

    def is_user_exist(self, email):
        user = self.db_conn.load_user(email)
        return user is not None


class User:

    def __init__(self, email, events):
        self.email = email
        self.events = events


class Event:

    def __init__(self, title, note, ts):
        self.title = title
        self.note = note
        self.ts = ts
