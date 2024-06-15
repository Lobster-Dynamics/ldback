import threading

from app import create_app

app = create_app()

threading.Thread(
    target=app.email_service.keep_smtp_connection_alive, daemon=True
).start()

app.run(host="0.0.0.0", debug=True)
