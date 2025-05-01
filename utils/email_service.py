import os
from email.message import EmailMessage
import smtplib
from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")
EMAIL_SUBJECT = os.getenv("EMAIL_SUBJECT")
MYTHOS360_UI = os.getenv("MYTHOS360_UI")

def send_login_email(to_email: str, name: str, password: str):
    msg = EmailMessage()
    msg["Subject"] = EMAIL_SUBJECT
    msg["From"] = SMTP_USER
    msg["To"] = to_email

    msg.set_content(f"""
Hi {name},

Welcome to Mythos360!

Your login credentials:
Email: {to_email}
Password: {password}

You can log in here: {MYTHOS360_UI}

Please change your password after logging in.

Best,
The Mythos360 Team
""")

    try:
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False
