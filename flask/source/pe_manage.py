from datetime import datetime

from pe_utils import get_hash

class Manager:

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_user(self, email, password):
        try:
            user_id = self.db_conn.store_user(email, password)
        except Exception as e:
            print(e)
            return None

        return user_id

    def get_user(self, email):
        user = self.db_conn.load_user(email)
        if not user:
            print(f'User does not exist. Email: {email}')

        return user

    def check_user_error(self, email, hash_password):
        user = self.get_user(email)
        if not user:
            return 'User does not exist'

        if hash_password != user['password']:
            return 'Incorrect email/password'

    def create_event(self, email, event):
        user = self.get_user(email)
        if not user:
            return None

        try:
            event_id = self.db_conn.store_event(user['id'], event)
        except Exception as e:
            print(e)
            return None

        return event_id

    def get_events(self, email):
        user = self.get_user(email)
        if not user:
            return []

        events = self.db_conn.load_events(user['id'])
        events = list(map(self.prepare_event, events))

        return events

    @staticmethod
    def prepare_event(event):
        event['date'] = datetime.utcfromtimestamp(int(event['ts'])).strftime('%Y-%m-%d %H:%M:%S')
        event['id'] = get_hash(''.join([str(event[key]) for key in ['id', 'title', 'ts']]))
        del event['ts']

        return event

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
