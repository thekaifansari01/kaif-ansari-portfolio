import os
import smtplib
from email.message import EmailMessage

SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
FROM_EMAIL = os.environ.get('NEWSLETTER_FROM', SMTP_USER)


def smtp_send(to_email, subject, text_body, html_body=None, reply_to=None):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError('SMTP not configured')
    if not FROM_EMAIL:
        raise RuntimeError('FROM_EMAIL not configured')

    msg = EmailMessage()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to_email
    if reply_to:
        msg['Reply-To'] = reply_to
    msg.set_content(text_body)
    if html_body:
        msg.add_alternative(html_body, subtype='html')

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)