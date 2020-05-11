FLASK_SECRET_KEY = 'me3kj32io2ori2k32j2i2r'

DB_HOST = '127.0.0.1'
DB_PORT = '5432'
DB_NAME = 'personal_events'
DB_USER = 'postgres'
DB_PWD = 'password'
DB_URL = f'postgresql://{DB_USER}:{DB_PWD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
