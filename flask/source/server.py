from flask import Flask, make_response, request, render_template, session
import logging
from time import time
from uuid import uuid4

from constants import FLASK_SECRET_KEY
from pe_db import DBConnecter, create_tables
from pe_mail import Mailer
from pe_manage import Manager
from pe_utils import get_hash_password

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

users = {}


@app.route('/', methods=['GET'])
def main():
    email = session['user'] if session.get('user') else None
    response = {
        'email': email,
        'events': manager.get_events(email) if email else []
    }

    return make_response(render_template('index.html', **response))


@app.route('/signin', methods=['POST'])
def sign_in():
    email = request.form.get('email')
    password = request.form.get('password')

    validation_error = manager.get_validation_error(email=email, password=password)
    if validation_error:
        return {'error': True, 'text': validation_error}

    hash_password = get_hash_password(password)
    error_text = manager.check_user_error(email, hash_password)
    if error_text:
        return {'error': True, 'text': error_text}

    session['user'] = email
    return {
        'error': False,
        'text':  f'Welcome back, {email}!',
        'email': email,
        'events': manager.get_events(email)
    }


@app.route('/signup', methods=['POST'])
def sign_up():
    email = request.form.get('email')
    password = request.form.get('password')

    validation_error = manager.get_validation_error(email=email, password=password)
    if validation_error:
        return {'error': True, 'text': validation_error}

    if manager.get_user(email) is not None:
        return {'error': True, 'text': 'User exists'}

    hash_password = get_hash_password(password)
    if not manager.create_user(email, hash_password):
        return {'error': True, 'text': 'Something went wrong'}

    session['user'] = email
    return


@app.route('/signout', methods=['POST'])
def sign_out():
    session.pop('user', None)
    return


@app.route('/set_event', methods=['POST'])
def set_event():
    if not session.get('user'):
        return {'error': True, 'text': 'User is not signed in'}

    email = session['user']
    event = {
        'ts': request.form.get('ts'),
        'tz': request.form.get('tz'),
        'title': request.form.get('title'),
        'note': request.form.get('note')
    }

    validation_error = manager.get_validation_error(**event)
    if validation_error:
        return {'error': True, 'text': validation_error}

    card_id = request.form.get('cardid')
    if card_id:
        if not manager.edit_event(card_id, event):
            return {'error': True, 'text': 'Something went wrong'}
        event['cardId'] = card_id
    else:
        event['cardId'] = f'{uuid4().hex}_{int(time())}'
        if not manager.create_event(email, event):
            return {'error': True, 'text': 'Something went wrong'}

    manager.prepare_event(event)

    return {'error': False, 'event': event}


@app.route('/delete_event', methods=['POST'])
def delete_event():
    if not session.get('user'):
        return {'error': True, 'text': 'User is not signed in'}

    email = session['user']
    card_id = request.form.get('cardId')

    if not manager.delete_event(email, card_id):
        return {'error': True, 'text': 'Something went wrong'}

    return {'error': False}


if __name__ == '__main__':
    logging.basicConfig(
        format=u'[%(asctime)s %(funcName)s:%(lineno)d] %(levelname)s %(message)s',
        datefmt='%Y%m%d %H:%M:%S'
    )
    logging.warning('start server')


    db_conn = DBConnecter()
    create_tables(db_conn.engine)
    manager = Manager(db_conn)
    mailer = Mailer(db_conn)
    app.run(port='5000')

