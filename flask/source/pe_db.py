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
            ts INTEGER NOT NULL,
            cardid VARCHAR(64) NOT NULL
        );
    ''')


class UserT(Base):
    __tablename__ = 'users'

    id = sa.Column(sa.INT, primary_key=True)
    email = sa.Column(sa.VARCHAR(128), nullable=False)
    password = sa.Column(sa.VARCHAR(128), nullable=False)


class EventT(Base):
    __tablename__ = 'events'

    id = sa.Column(sa.INT, primary_key=True)
    userid = sa.Column(sa.INT, nullable=False)
    title = sa.Column(sa.VARCHAR(64), nullable=False)
    note = sa.Column(sa.TEXT, nullable=False)
    ts = sa.Column(sa.DATETIME, nullable=False)
    cardid = sa.Column(sa.VARCHAR(64))


class DBConnecter:

    def __init__(self):
        self.engine = sa.create_engine(DB_URL)
        self.DBSession = sessionmaker(bind=self.engine)

    def store_user(self, email, password):
        user_t = UserT(
            email=email,
            password=password,
        )
        return self._store(user_t)

    def load_user(self, email):
        session = self.DBSession()
        row = session.query(UserT).filter(UserT.email == email).first()
        session.close()

        return {
            'id': row.id,
            'email': row.email,
            'password': row.password
        } if row else None

    def store_event(self, user_id, event):
        event_t = EventT(
            userid=user_id,
            title=event['title'],
            note=event['note'],
            ts=event['ts'],
            cardid=event['cardId'],
        )
        return self._store(event_t)

    def load_events(self, user_id):
        session = self.DBSession()
        rows = session.query(EventT)\
            .filter(EventT.userid == user_id)\
            .order_by(EventT.ts)\
            .all()
        session.close()

        events = []
        for row in rows:
            events.append({
                'id': row.id,
                'title': row.title,
                'note': row.note,
                'ts': row.ts,
                'cardId': row.cardid,
            })
            
        return events

    def _store(self, obj):
        session = self.DBSession()
        try:
            session.add(obj)
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            obj_id = obj.id
            session.close()
            return obj_id
