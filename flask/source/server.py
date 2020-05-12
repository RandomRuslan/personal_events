from flask import Flask, make_response, request, render_template, session

from constants import FLASK_SECRET_KEY
from pe_db import DBConnecter, create_tables
from pe_manage import Manager
from pe_utils import get_hash_password

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

users = {}


@app.route('/', methods=['GET'])
def main():
    if session.get('user'):
        email = session['user']
        main_message = f'Hello, {email}'
    else:
        main_message = 'You should sign in'

    return make_response(render_template('index.html', **{'main_message': main_message}))


@app.route('/signin', methods=['POST'])
def sign_in():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return {'error': True, 'text': 'Auth data is required!'}

    hash_password = get_hash_password(password)
    error_text = manager.check_user_error(email, hash_password)
    if error_text:
        return {'error': True, 'text': error_text}

    session['user'] = email
    return {'error': False, 'text':  f'Welcome back, {email}!'}


@app.route('/signup', methods=['POST'])
def sign_up():
    email = request.form.get('email')
    password = request.form.get('password')

    if not email or not password:
        return {'error': True, 'text': 'Auth data is required!'}

    if manager.is_user_exist(email):
        return {'error': True, 'text': 'User exists'}

    hash_password = get_hash_password(password)
    if not manager.create_user(email, hash_password):
        return {'error': True, 'text': 'Somesing went wrong. Try again'}

    session['user'] = email
    return {'error': False, 'text': f'Welcome, {email}!'}


@app.route('/', methods=['POST'])
def post():
    email = request.form.get('email')
    password = request.form.get('password')

    text = ''
    error = False
    response = {'error': False}

    if not email or not password:
        error = True
        text = 'Auth data is required!'
        return response

    hash_password = get_hash_password(password)

    if email in users:
        print(email, users[email], session.get('user'))
        if users[email][0] == hash_password:
            session['user'] = email
            users[email][1] += 1
            text = 'Welcome back, {}. {} times'.format(email, users[email][1])
        else:
            error = True
            text = 'Wrong username/password'
    else:
        users[email] = [hash_password, 0]
        session['user'] = email
        text = 'Hello, {}'.format(email)

    return {
        'error': error,
        'text': text
    }


if __name__ == '__main__':
    db_conn = DBConnecter()
    manager = Manager(db_conn)
    create_tables(db_conn.engine)
    app.run(port='5000')

