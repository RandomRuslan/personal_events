import hashlib

from constants import PWD_SALT

def get_hash_password(password):
    password += PWD_SALT
    return hashlib.sha256(password.encode('utf-8')).hexdigest()
