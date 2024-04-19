import logging
from flask_socketio import SocketIO
import handlers
import json

from flask import Flask, send_from_directory
app = Flask(__name__)
socketio = SocketIO(app, debug=app.debug, cors_allowed_origin="*", allowEIO3=True )

logFormatter = logging.Formatter("%(levelname)s | %(asctime)s | %(message)s")
rootLogger = logging.getLogger()
rootLogger.setLevel(logging.DEBUG if app.debug else logging.INFO)

fileHandler = logging.FileHandler("main.log")
fileHandler.setFormatter(logFormatter)
rootLogger.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
rootLogger.addHandler(consoleHandler)



handlers.initialize_plex(app.debug)


@app.route('/')
def getHome():
    return handlers.return_home()

@app.route('/debug')
def isDebug():
    return str(app.debug)

    

@app.route("/static/<path:path>", methods=['GET'])
def staticFiles(path):
    return send_from_directory('static', path)

# @app.route("/favicon.ico", methods=['GET'])
# def icon():
#     return send_from_directory('static', "favicon.ico")
    
# @app.route("/library/<id>", methods=['POST'])
# def save_to_library(id):
#     pass

@socketio.on("intialize")
def initialize(data):
    return handlers.initialize_file(data, socketio)

@socketio.on("upload")
def stream_upload(file_id, buffer):
    return handlers.stream_upload(file_id, buffer, socketio)

@socketio.on("cleanup")
def cleanup_file(file_id, library_id):
    return handlers.cleanup_file(file_id=file_id, library_id=library_id, socket=socketio)

