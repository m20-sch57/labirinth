# encoding: utf-8

from app import app, dbase, socketio, labyrinths_list
from flask_socketio import emit, join_room, leave_room
from flask import render_template, request, session, redirect, url_for, send_file
from functools import wraps
from hashlib import sha1
import random, string, json, io, sys

from labyrinth_test import generate_labyrinth

sys.path.append('..')


def login_required(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        if session.get('username') is None:
            return redirect(url_for('index'))
        else:
            return f(*args, **kwargs)
    return wrapped


def simple_render_template(url, **kwargs):
    return render_template(url, username=session.get('username'), **kwargs)


@app.route('/')
@app.route('/index')
def index():
    return simple_render_template('index.html', reg_error=False)


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')

        if not dbase.user_login_in_table(username) or \
                dbase.get_user_password_hash(username) != sha1(password.encode('utf-8')).hexdigest():
            return redirect(url_for('login_failed'))

        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login_register/login.html')


@app.route('/logout')
@login_required
def logout():
    session.pop('username', None)
    return redirect(url_for('index'))


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        username = request.form.get('login')
        password = request.form.get('password')

        if not dbase.add_user(username, sha1(password.encode('utf-8')).hexdigest()):
            return redirect(url_for('register_failed'))

        session['username'] = username
        return redirect(url_for('index'))
    return render_template('login_register/register.html')


@app.route('/login_failed')
def login_failed():
    return render_template('index.html', username=None, reg_error=True)


@app.route('/register_failed')
def register_failed():
    return render_template('login_register/register_failed.html')


@app.route('/profile')
@login_required
def profile():
    username = session.get('username')
    return simple_render_template('profile.html')


@app.route('/room_list/<page>', methods=['POST', 'GET'])
def room_list(page):
    if request.method == 'POST':
        room_id = request.form.get('join_button')
        return redirect(url_for('waiting_room', room_id=room_id))
    return simple_render_template('rooms/room_list.html', pager=dbase.get_rooms_page_by_page()[int(page)])


@app.route('/rules')
def rules():
    return simple_render_template('rules.html')


@app.route('/create_room')
@login_required
def create_room():
    def genereate_room_id(size):
        return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(size))
    room_id = genereate_room_id(8)
    dbase.add_room(room_id, session.get('username'))
    return redirect(url_for('waiting_room', room_id=room_id))


@app.route('/waiting_room/<room_id>', methods=['POST', 'GET'])
@login_required
def waiting_room(room_id):
    if request.method == 'POST':
        event_type = request.headers.get('Event-Type')

        if event_type == 'change_name':
            name = request.form.get('new_name')
            dbase.set_room_name(room_id, name)
            emit('update', {'event': 'change_name', 'name': name},
                 broadcast=True, room=room_id, namespace='/wrws')

        elif event_type == 'change_description':
            description = request.form.get('new_description')
            dbase.set_description(room_id, description)
            emit('update', {'event': 'change_description', 'description': description},
                 broadcast=True, room=room_id, namespace='/wrws')

        elif event_type == 'start_game':
            labyrinth = generate_labyrinth(dbase.get_room_players(room_id), room_id)
            labyrinths_list.add_labyrinth(room_id, labyrinth)
            emit('update', {'event': 'start_game'},
                 broadcast=True, room=room_id, namespace='/wrws')

    username = session.get('username')
    labyrinth = labyrinths_list.get_labyrinth(room_id)
    if labyrinth is not None and username in [user.get_username() for user in labyrinth.players_list]:
        return redirect(url_for('game_room', room_id=room_id))
    else:
        return simple_render_template('rooms/waiting_room.html', room=dbase.get_room(room_id), hide_header=True)


@app.route('/game_room/<room_id>', methods=['POST', 'GET'])
def game_room(room_id):
    username = session.get('username')
    labyrinth = labyrinths_list.get_labyrinth(room_id)
    if request.method == 'POST':
        event_type = request.headers.get('Event-Type')

        if event_type == 'update':

            buttons = [
                {'type': 'button', 'turn': 'Идти вверх', 'image': url_for('static', filename='res/button_images/up.png')},
                {'type': 'button', 'turn': 'Идти вниз', 'image': url_for('static', filename='res/button_images/down.png')}
            ]

            msg = labyrinth.player_to_send(username)
            ats = labyrinth.get_active_player_ats()
            if labyrinth.get_active_player_username() == username:
                return json.dumps({'your_turn': 'yes', 'msg': msg, 'ats': ats, 'buttons': buttons})
            else:
                return json.dumps({'your_turn': 'no', 'msg': msg})

        elif event_type == 'turn':
            if labyrinth.get_active_player_username() == username:
                turn = request.form.get('turn')
                labyrinth.make_turn(turn)
                emit('update', {'event': 'player_make_turn'},
                     broadcast=True, room=room_id, namespace='/grws')
    if labyrinth is None or username not in [user.get_username() for user in labyrinth.players_list]:
        return redirect(url_for('waiting_room', room_id=room_id))
    else:
        return simple_render_template('rooms/game_room.html', room=dbase.get_room(room_id), hide_header=True)


@socketio.on('player join', namespace='/grws')
@socketio.on('player join', namespace='/wrws')
def wrws_pj(msg):
    room_id = msg['room_id']
    username = session.get('username')

    join_room(room_id)
    dbase.add_player(room_id, username)
    emit('update', {'event': 'player_enter_or_leave', 'players': ','.join(dbase.get_room_players(room_id))},
         broadcast=True, room=room_id, namespace='/wrws')

    session['room'] = room_id


@socketio.on('disconnect', namespace='/grws')
@socketio.on('disconnect', namespace='/wrws')
def wrws_pl():
    room_id = session.get('room')
    username = session.get('username')

    leave_room(room_id)
    dbase.remove_player(room_id, username)
    emit('update', {'event': 'player_enter_or_leave', 'players': ','.join(dbase.get_room_players(room_id))},
         broadcast=True, room=room_id, namespace='/wrws')

    session.pop('room', None)

