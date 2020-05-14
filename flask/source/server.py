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
    text = None
    if session.get('user'):
        email = session['user']
    else:
        text = 'You should sign in'
        email = None

    response = {
        'email': email,
        'text': text
    }
    print(response)
    return make_response(render_template('index.html', **response))


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
    return {'error': False, 'text':  f'Welcome back, {email}!', 'email': email}


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
    return {'error': False, 'text': f'Welcome, {email}!', 'email': email}


@app.route('/signout', methods=['POST'])
def sign_out():
    session.pop('user', None)
    return {'text': 'You should sign in'}

@app.route('/add_event', methods=['POST'])
def add_event():
    return {'text': 'OK'}


if __name__ == '__main__':
    db_conn = DBConnecter()
    manager = Manager(db_conn)
    create_tables(db_conn.engine)
    app.run(port='5000')

