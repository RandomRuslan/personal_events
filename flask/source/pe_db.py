import json
from datetime import datetime

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from constants import DB_URL


Base = declarative_base()


def create_tables(engine):
    engine.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL,
            email VARCHAR(128) UNIQUE NOT NULL,
            password VARCHAR(128) UNIQUE NOT NULL
        );
    ''')

    engine.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL,
            userid INTEGER NOT NULL,
            title VARCHAR(64) NOT NULL,
            note TEXT NOT NULL,
            eventts TIMESTAMP NOT NULL,
            creationts TIMESTAMP NOT NULL
        );
    ''')


class DBConnecter:

    def __init__(self):
        self.engine = sa.create_engine(DB_URL)
        self.DBSession = sessionmaker(bind=self.engine)
