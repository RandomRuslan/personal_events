import logging
import re

from pe_utils import convert_ts_to_date


class Manager:

    def __init__(self, db_conn):
        self.db_conn = db_conn

    def create_user(self, email, password):
        try:
            user_id = self.db_conn.store_user(email, password)
        except Exception as e:
            logging.exception(e)
            return None

        return user_id

    def get_user(self, email):
        user = self.db_conn.load_user(email)
        if not user:
            logging.error(f'User does not exist. Email: {email}')

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
            logging.exception(e)
            return None

        return event_id

    def edit_event(self, card_id, event):
        event['notified'] = False
        try:
            self.db_conn.edit_event(card_id, event)
        except Exception as e:
            logging.exception(e)
            return False

        return True

    def delete_event(self, email, card_id):
        user = self.get_user(email)
        if not user:
            return False

        try:
            self.db_conn.delete_event(user['id'], card_id)
        except Exception as e:
            logging.exception(e)
            return False

        return True

    def get_events(self, email):
        user = self.get_user(email)
        if not user:
            return []

        events = self.db_conn.load_events(user['id'])
        events = list(map(self.prepare_event, events))

        return events

    @staticmethod
    def prepare_event(event):
        event['date'] = convert_ts_to_date(event['ts'], event['tz'])

        event.pop('id', None)
        event.pop('tz', None)

        return event

    @staticmethod
    def get_validation_error(**data):
        
        def get_readable_key(key):
            if key == 'ts':
                return 'Date'
            return key[0].upper() + key[1:]
        
        error = []

        int_required = ['ts', 'tz']
        key_to_max = {
            'ts': 253402289940,  # 9999-12-31 23:59:00
            'tz': 12
        }
        key_to_min = {
            'ts': 0,    # 1970-01-01 00:00:00
            'tz': -12
        }
        key_to_len = {
            'email': 128,
            'password': 64,
            'title': 64,
            'note': 32000
        }
        key_to_regex = {
            'email': r'[^@]+@[^@]+\.[^@]+'
        }

        for key, value in data.items():
            if key in int_required:
                try:
                    int(value)
                except ValueError:
                    error.append(f'{key} must be number')
                    continue

            if not value:
                error.append(f'{get_readable_key(key)} is required')
            elif key in key_to_len and len(value) > key_to_len[key]:
                error.append(f'{get_readable_key(key)} is too long (max={key_to_len[key]})')
            elif key in key_to_regex and not re.match(key_to_regex[key], value):
                error.append(f'Incorrect format of {key}')
            elif key in key_to_max and key_to_max[key] < int(value):
                error.append(f'{get_readable_key(key)} is too big')
            elif key in key_to_min and key_to_min[key] > int(value):
                error.append(f'{get_readable_key(key)} is too small')

        return '\n'.join(error) if error else None
