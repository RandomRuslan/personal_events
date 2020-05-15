class Manager:

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_user(self, email, password):
        try:
            self.db_conn.store_user(email, password)
        except Exception as e:
            print(e)
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

    def create_event(self, email, event):
        user = self.db_conn.load_user(email)
        if not user:
            print('no-user')
            return False

        try:
            self.db_conn.store_event(user['id'], event)
        except Exception as e:
            print(e)
            return False

        return True

    @staticmethod
    def get_validation_error(**data):
        error = []
        int_required = ['ts']
        key_to_len = {
            'email': 128,
            'password': 64,
            'title': 64,
            'note': 32000
        }

        for key, value in data.items():
            if not value:
                error.append(f'{key} is required')
            elif key in key_to_len and len(value) > key_to_len[key]:
                error.append(f'{key} is too long (max={key_to_len[key]})')
            else:
                if key in int_required:
                    try:
                        int(value)
                    except ValueError:
                        error.append(f'{key} must be number')

        return '\n'.join(error) if error else None


class User:

    def __init__(self, email, events):
        self.email = email
        self.events = events


class Event:

    def __init__(self, title, note, ts):
        self.title = title
        self.note = note
        self.ts = ts
