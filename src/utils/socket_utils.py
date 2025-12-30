from plugins.socket_plugin import get_socketio
from domain.constants import ManagerRoom

def emit_to_manager(event, data):
    """Emit event to manager room"""
    socketio = get_socketio()
    if socketio:
        socketio.emit(event, data, room=ManagerRoom)

def emit_to_socket(socket_id, event, data):
    """Emit event to specific socket"""
    socketio = get_socketio()
    if socketio and socket_id:
        socketio.emit(event, data, room=socket_id)

def emit_to_manager_and_socket(socket_id, event, data):
    """Emit event to manager room and specific socket"""
    socketio = get_socketio()
    if socketio:
        socketio.emit(event, data, room=ManagerRoom)
        if socket_id:
            socketio.emit(event, data, room=socket_id)

