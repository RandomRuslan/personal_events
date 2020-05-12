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
            eventts TIMESTAMP NOT NULL
        );
    ''')


class UserT(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.INT, primary_key=True)
    email = sa.Column(sa.VARCHAR(128), nullable=False)
    password = sa.Column(sa.VARCHAR(128), nullable=False)


class EventsT(Base):
    __tablename__ = 'events'

    id = sa.Column(sa.INT, primary_key=True)
    userid = sa.Column(sa.INT, nullable=False)
    title = sa.Column(sa.VARCHAR(64), nullable=False)
    note = sa.Column(sa.TEXT, nullable=False)
    eventts = sa.Column(sa.DATETIME, nullable=False)


class DBConnecter:

    def __init__(self):
        self.engine = sa.create_engine(DB_URL)
        self.DBSession = sessionmaker(bind=self.engine)

    def store_user(self, email, password):
        user = UserT(
            email=email,
            password=password,
        )
        self._store(user)

    def load_user(self, email):
        session = self.DBSession()
        row = session.query(UserT).filter(UserT.email == email).first()
        session.close()

        return {
            'email': row.email,
            'password': row.password
        } if row else None

    def _store(self, obj):
        session = self.DBSession()
        try:
            session.add(obj)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
