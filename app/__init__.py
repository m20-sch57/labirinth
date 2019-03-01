from flask import Flask, request
from database import Database
from labyrinths_list import LabyrinthsList
from flask_socketio import SocketIO

app = Flask(__name__)
app.config['SECRET_KEY'] = "Your_secret_string"
socketio = SocketIO(app)

dbase = Database()
labyrinths_list = LabyrinthsList()

from app import routes

socketio.run(app, host="0.0.0.0", port=3000, debug=True)
