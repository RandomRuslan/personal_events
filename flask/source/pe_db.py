import logging
from time import time
from typing import Dict, List, Union, NoReturn

import sqlalchemy as sa
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


from constants import DB_URL


Base = declarative_base()


def create_tables(engine) -> NoReturn:
    engine.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL,
            email VARCHAR(128) UNIQUE NOT NULL,
            password VARCHAR(128) NOT NULL
        );
    ''')

    engine.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id SERIAL,
            userid INTEGER NOT NULL,
            title VARCHAR(64) NOT NULL,
            note TEXT NOT NULL,
            ts BIGINT NOT NULL,
            tz INTEGER NOT NULL,
            cardid VARCHAR(64) NOT NULL,
            notified BOOLEAN DEFAULT FALSE
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
    ts = sa.Column(sa.BIGINT, nullable=False)
    tz = sa.Column(sa.INT, nullable=False)
    cardid = sa.Column(sa.VARCHAR(64))
    notified = sa.Column(sa.BOOLEAN, default=False)


class DBConnecter:

    def __init__(self):
        self.engine = sa.create_engine(DB_URL)
        self.DBSession = sessionmaker(bind=self.engine)

    def store_user(self, email: str, password: str) -> Union[int, None]:
        user_t = UserT(
            email=email,
            password=password,
        )
        return self._store(user_t)

    def load_user(self, email: str) -> Union[Dict, None]:
        session = self.DBSession()
        row = session.query(UserT).filter(UserT.email == email).first()
        session.close()

        return {
            'id': row.id,
            'email': row.email,
            'password': row.password
        } if row else None

    def store_event(self, user_id: int, event: dict) -> Union[int, None]:
        event_t = EventT(
            userid=user_id,
            title=event['title'],
            note=event['note'],
            ts=event['ts'],
            tz=event['tz'],
            cardid=event['cardId'],
        )
        return self._store(event_t)

    def edit_event(self, card_id: str, event: Dict) -> NoReturn:
        session = self.DBSession()
        session.query(EventT).filter(EventT.cardid == card_id).update(event)
        session.commit()
        session.close()

    def delete_event(self, user_id: int, card_id: str) -> NoReturn:
        session = self.DBSession()
        session.delete(
            session.query(EventT)
            .filter(EventT.userid == user_id)
            .filter(EventT.cardid == card_id)
            .one()
        )
        session.commit()
        session.close()

    def load_events(self, user_id: int) -> List[Dict]:
        session = self.DBSession()
        rows = session.query(EventT)\
            .filter(EventT.userid == user_id)\
            .order_by(sa.desc(EventT.ts))\
            .all()
        session.close()

        events = []
        for row in rows:
            events.append({
                'id': row.id,
                'title': row.title,
                'note': row.note,
                'ts': row.ts,
                'tz': row.tz,
                'cardId': row.cardid,
            })
            
        return events

    def load_events_for_mailing(self) -> List[Dict]:
        now = int(time())

        session = self.DBSession()
        rows = session.query(EventT).join(UserT, UserT.id == EventT.userid)\
            .with_entities(UserT.email, EventT.id, EventT.title, EventT.note, EventT.ts, EventT.tz, EventT.cardid)\
            .filter(EventT.notified.is_(False))\
            .filter(EventT.ts >= now)\
            .filter(EventT.ts <= now + 60 * 60)\
            .all()

        session.close()

        events = []
        for row in rows:
            events.append({
                'email': row.email,
                'title': row.title,
                'note': row.note,
                'ts': row.ts,
                'tz': row.tz,
                'cardId': row.cardid
            })

        return events

    def _store(self, obj: Union[UserT, EventT]) -> Union[int, None]:
        session = self.DBSession()
        try:
            session.add(obj)
            session.commit()
        except Exception as e:
            logging.exception(e)
            session.rollback()
            raise
        finally:
            obj_id = obj.id
            session.close()
            return obj_id
