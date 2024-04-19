from flask import render_template
from flask_socketio import SocketIO
import os
import re
from plex import PlexAPI
from decompression import Decompressor
import logging
import pathlib

temp_path = os.environ.get('TEMP_PATH', "./tmp")
plex_client: PlexAPI
isDebug: bool
def initialize_plex(debug: bool=False):
    global plex_client, isDebug
    isDebug = debug
    if debug:
        plex_client =  PlexAPI(os.environ.get("X_PLEX_TOKEN"))
    else:
        plex_client =  PlexAPI(os.environ.get("X_PLEX_TOKEN"), base_url='plex')

def return_home():
    
    context = {
        "libraries": plex_client.get_libraries()
    }

    return render_template('index.html', **context)

def initialize_file(file_id, socket:SocketIO):

    pathlib.Path(os.path.join(temp_path, file_id + ".tmp")).touch()
    processed_files[file_id] = 0

    logging.info(f"File {file_id} initialized")
    socket.emit(f"initialized-{file_id}")

processed_files = {}

def stream_upload(file_id, buffer, socket: SocketIO):
    logging.info(f"New data recived for file {file_id}, processing")

    with open(os.path.join(temp_path, file_id + ".tmp"), 'wb') as tmp_file:
        bytes_written = tmp_file.write(buffer)
        logging.debug("Bytes written: %d", bytes_written)
    socket.emit(f'data_recieved-{file_id}') # Emit number of bytes processed
    return ""
    

def cleanup_file(file_id, library_id, socket:SocketIO):
    _update_library(library_id=library_id, file_id=file_id)

    logging.info(f"Cleaning up file processing for {file_id}")
    socket.emit(f'cleanup_finished-{file_id}')
    return ""
    

def _update_library(library_id="", file_id="" ):
    libraries = plex_client.get_libraries()
    library = [library for library in libraries if library.get('key') == library_id][0]

    logging.debug(library["path"])
    
    Decompressor.decompress(os.path.join(temp_path, file_id + ".tmp"), os.path.join(library["path"], file_id))
    try:
        os.unlink(os.path.join(temp_path, file_id + ".tmp"))
        pass
    except Exception as e:
        logging.warning(e)

    plex_client.refresh_library(library["key"])
    return ""