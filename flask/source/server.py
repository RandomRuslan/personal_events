from flask import Flask, make_response, request, render_template, session

from constants import FLASK_SECRET_KEY
from pe_db import DBConnecter, create_tables

app = Flask(__name__)
app.secret_key = FLASK_SECRET_KEY

users = {}
"""
    user_id: [password, event_count]
"""


@app.route('/', methods=['GET'])
def main():
    print('HELLO')
    if session.get('user'):
        user = session['user']
        print(user)
        if user in users:
            text = users[user][1]
        # get_events(request.cookies['user'])
    else:
        # get_auth(request)
        pass

    return make_response(render_template('index.html', **{'text': 'main'}))


@app.route('/', methods=['POST'])
def post():
    user = request.form.get('username')
    password = request.form.get('password')

    text = ''
    error = False
    response = {'error': False}

    if not user or not password:
        error = True
        text = 'Auth data is required!'
        return response

    if user in users:
        if users[user][0] == password:
            session['user'] = user
            users[user][1] += 1
            text = 'Welcome back, {}. {} times'.format(user, users[user][1])
        else:
            error = True
            text = 'Wrong username/password'
    else:
        users[user] = [password, 0]
        session['user'] = user
        text = 'Hello, {}'.format(user)

    return {
        'error': error,
        'text': text
    }


def get_events(user):
    text = 'All'
    response = make_response(render_template('index.html', text=text))
    response.set_cookie('username', 'the username')
    return response


if __name__ == '__main__':
    db_conn = DBConnecter()
    create_tables(db_conn.engine)
    app.run(port='5000')

