from flask import Flask, request
from flask_socketio import SocketIO, emit, send
import logging
import os
from Communication import Communication

app = Flask(__name__)
socketio = SocketIO(app)

currentusers = {}

logger_path = "./logs"
# create folder if it doesn't exist
if not os.path.exists(logger_path):
    os.makedirs(logger_path)

logger_name = "server.log"
logger = logging.getLogger(logger_name)
logger.setLevel(logging.ERROR)
fh = logging.FileHandler(logger_path + "/" + logger_name)
fh.setLevel(logging.ERROR)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.log(logging.INFO, f"Server - created")

@socketio.on('connect')
def on_connect(data):
    logger.log(logging.INFO, f"Client connected - {request.sid}")

@socketio.on('join')
def on_join(data):
    currentusers[data["name"]] = request.sid
    emit('joined', {'data': currentusers})

@socketio.on('sendmessage')
def on_sendmessage(data):
    logger.log(logging.INFO, f"Message received - {data['message']}")
    emit('message', {'message': data['message']}, to=currentusers[data['to']])

if __name__ == '__main__':
    socketio.run(app, debug=True, host='127.0.0.1', port=3000)