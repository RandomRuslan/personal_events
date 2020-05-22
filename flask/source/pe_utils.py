import hashlib
from threading import Timer
from datetime import datetime

from constants import PWD_SALT


def get_hash_password(value):
    value += PWD_SALT
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def convert_ts_to_date(ts, tz):
    ts = int(ts) - int(tz) * 60 * 60
    date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S').split()

    return date


class Repeater:

    def __init__(self, period, repetitive_function):
        self.period = period
        self.repetitive_function = repetitive_function
        self.thread = Timer(self.period, self.handle_function)

    def handle_function(self):
        self.repetitive_function()
        self.thread = Timer(self.period, self.handle_function)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()