from create_app import create_app
from plugins.socket_plugin import get_socketio
import os

app, socketio = create_app()

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 4000))
    # Disable debug in production
    debug = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    socketio.run(app, host="0.0.0.0", port=port, debug=debug)

