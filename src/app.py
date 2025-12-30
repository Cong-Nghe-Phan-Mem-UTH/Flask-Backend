from create_app import create_app
from plugins.socket_plugin import get_socketio

app, socketio = create_app()

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=4000, debug=True)

