from create_app import create_app
from plugins.socket_plugin import get_socketio
import os
import sys

app, socketio = create_app()

if __name__ == "__main__":
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 4000))
    # Disable debug in production
    debug = os.environ.get('DEBUG', 'False').lower() in ['true', '1']
    
    # Print startup info for debugging
    print(f"🚀 Starting Flask app on port {port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🌐 Environment: {'Production' if os.environ.get('PRODUCTION', 'false').lower() == 'true' else 'Development'}")
    
    try:
        socketio.run(app, host="0.0.0.0", port=port, debug=debug, use_reloader=False)
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

