from datetime import datetime
import hashlib
from threading import Timer
from typing import List, Union

from constants import PWD_SALT


def get_hash_password(value: str) -> str:
    value += PWD_SALT
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


def convert_ts_to_date(ts: Union[int, str], tz: Union[int, str]) -> List[str]:
    ts = int(ts) - int(tz) * 60 * 60
    date = datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M').split()

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