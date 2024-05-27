import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from queue import Queue

from application.email.iemail import IEMAIL

SMTP_SERVER = "mail.privateemail.com"
SMTP_PORT = 465
SMTP_USERNAME = "fridaresearch@frida-backend.me"
SMTP_PASSWORD = "contrasena123R"


class EmailService(IEMAIL):

    def __init__(self):
        self.smtp_connection = None
        self.email_queue = Queue()

    def keep_smtp_connection_alive(self):
        while True:
            try:
                if self.smtp_connection is None:
                    print("Connecting to the SMTP server...")
                    self.smtp_connection = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT)
                    self.smtp_connection.login(SMTP_USERNAME, SMTP_PASSWORD)
                    print("Connected to the SMTP server.")
                else:
                    self.smtp_connection.noop()

                while not self.email_queue.empty():
                    email_data = self.email_queue.get()
                    self.send_email_via_smtp(email_data)

            except Exception as e:
                print(f"Failed to keep SMTP connection alive: {e}")
                self.smtp_connection = None

            time.sleep(60)

    def send_email_via_smtp(self, email_data):

        if self.smtp_connection:

            try:
                msg = MIMEMultipart()
                msg["From"] = SMTP_USERNAME
                msg["To"] = email_data["to_email"]
                msg["Subject"] = email_data["subject"]
                msg.attach(MIMEText(email_data["body"], "plain"))

                self.smtp_connection.sendmail(
                    SMTP_USERNAME, email_data["to_email"], msg.as_string()
                )

                print(f"Email sent successfully to {email_data['to_email']}")

            except Exception as e:
                print(f"Failed to send email: {e}")
                self.email_queue.put(email_data)
                self.smtp_connection = None

        else:
            self.email_queue.put(email_data)
            print(
                f"Email queued for {email_data['to_email']} due to no SMTP connection"
            )

    def send_email(self, subject: str, body: str, to_email: str):
        email_data = {"subject": subject, "body": body, "to_email": to_email}

        if self.smtp_connection:
            self.send_email_via_smtp(email_data)
        else:
            self.email_queue.put(email_data)
            print(f"Email queued for {to_email} due to no SMTP connection")
