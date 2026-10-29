import os
import requests

RESEND_API_KEY = os.environ.get('RESEND_API_KEY')
FROM_EMAIL = os.environ.get('NEWSLETTER_FROM', 'kaif@kaifansari.me')
RESEND_URL = 'https://api.resend.com/emails'


def smtp_send(to_email, subject, text_body, html_body=None, reply_to=None):
    if not RESEND_API_KEY:
        raise RuntimeError('RESEND_API_KEY not configured')
    if not FROM_EMAIL:
        raise RuntimeError('FROM_EMAIL not configured')

    payload = {
        'from': FROM_EMAIL,
        'to': [to_email],
        'subject': subject,
        'text': text_body,
    }
    if html_body:
        payload['html'] = html_body
    if reply_to:
        payload['reply_to'] = reply_to

    headers = {
        'Authorization': f'Bearer {RESEND_API_KEY}',
        'Content-Type': 'application/json',
    }

    try:
        res = requests.post(RESEND_URL, json=payload, headers=headers, timeout=10)
    except Exception as e:
        raise RuntimeError(f'Resend network error: {e}')

    if res.status_code not in (200, 201):
        raise RuntimeError(f'Resend error {res.status_code}: {res.text[:200]}')