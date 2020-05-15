import hashlib

from constants import ID_SALT, PWD_SALT


def get_hash(value, is_password=False):
    value += PWD_SALT if is_password else ID_SALT
    return hashlib.sha256(value.encode('utf-8')).hexdigest()
