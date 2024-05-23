import smtplib
import threading
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import Flask, jsonify, request

app = Flask(__name__)

# SMTP server configuration
SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 465
SMTP_USERNAME = "fridaresearch@frida-backend.me"
SMTP_PASSWORD = "contrasena123R"

# Global SMTP connection
smtp_connection = None


def keep_smtp_connection_alive():
    global smtp_connection
    while True:
        try:
            if smtp_connection is None:
                print("Connecting to the SMTP server...")
                smtp_connection = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
                smtp_connection.login(SMTP_USERNAME, SMTP_PASSWORD)
                print("Connected to the SMTP server.")
            else:
                # Send a NOOP command to keep the connection alive
                smtp_connection.noop()
        except Exception as e:
            print(f"Failed to keep SMTP connection alive: {e}")
            smtp_connection = None

        # Wait for 1 minute before checking the connection again
        time.sleep(60)


# Start the background thread to keep the SMTP connection alive
threading.Thread(target=keep_smtp_connection_alive, daemon=True).start()


@app.route("/send_email", methods=["POST"])
def send_email():
    global smtp_connection

    if smtp_connection is None:
        return jsonify({"error": "SMTP connection is not available"}), 500

    try:
        data = request.json
        subject = data.get("subject")
        body = data.get("body")
        to_email = data.get("to_email")

        msg = MIMEMultipart()
        msg["From"] = SMTP_USERNAME
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        smtp_connection.sendmail(SMTP_USERNAME, to_email, msg.as_string())
        return jsonify({"message": "Email sent successfully!"}), 200

    except Exception as e:
        return jsonify({"error": f"Failed to send email: {e}"}), 500


if __name__ == "__main__":
    app.run(debug=True)
