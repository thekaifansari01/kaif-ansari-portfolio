import json
import os
import secrets
import smtplib
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler

import requests

SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
FROM_EMAIL = os.environ.get('NEWSLETTER_FROM', SMTP_USER)
SITE_URL = os.environ.get('SITE_URL', 'https://kaifansari.me').rstrip('/')

UPSTASH_URL = os.environ.get('UPSTASH_REDIS_REST_URL')
UPSTASH_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN')

ALLOWED_ORIGINS = [o.strip() for o in os.environ.get('ALLOWED_ORIGINS', SITE_URL).split(',') if o.strip()]


def redis_cmd(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    try:
        res = requests.post(
            UPSTASH_URL.rstrip('/'),
            headers={
                'Authorization': f'Bearer {UPSTASH_TOKEN}',
                'Content-Type': 'application/json',
            },
            json=[str(a) for a in args],
            timeout=5,
        )
        if res.status_code != 200:
            return None
        return res.json().get('result')
    except Exception:
        return None


def get_client_ip(handler):
    ip = handler.headers.get('x-real-ip')
    if not ip:
        xff = handler.headers.get('x-forwarded-for', '')
        ip = xff.split(',')[0].strip() if xff else ''
    return ip or 'unknown'


def cors_origin(handler):
    origin = handler.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        return origin
    return ALLOWED_ORIGINS[0] if ALLOWED_ORIGINS else SITE_URL


def verify_turnstile(token, ip):
    if not token:
        return False
    try:
        r = requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={'secret': SECRET_KEY, 'response': token, 'remoteip': ip},
            timeout=5,
        )
        return r.json().get('success', False)
    except Exception:
        return False


def rate_limit(ip):
    key = f'rl:nl:{ip}'
    count = redis_cmd('incr', key)
    if count is None:
        return True
    try:
        count = int(count)
    except (TypeError, ValueError):
        return False
    if count == 1:
        redis_cmd('expire', key, 3600)
    return count <= 5


def send_confirmation(email, token):
    if not SMTP_USER or not SMTP_PASS:
        raise RuntimeError('SMTP not configured')
    if not FROM_EMAIL:
        raise RuntimeError('FROM_EMAIL not configured')

    link = f'{SITE_URL}/api/confirm?token={token}'

    msg = EmailMessage()
    msg['Subject'] = 'Confirm your subscription - kaif ansari'
    msg['From'] = FROM_EMAIL
    msg['To'] = email
    msg['Reply-To'] = FROM_EMAIL
    msg['X-Mailer'] = 'kaif-portfolio-newsletter'

    plain = f"""Confirm your subscription

You're one click away from build logs, new agents, and things I break at 2am.

Confirm here:
{link}

Link expires in 24 hours.

If you didn't request this, ignore this email.

~/
kaif
{SITE_URL}
"""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>Confirm your subscription</title>
</head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,Helvetica,sans-serif;">
<div style="display:none;max-height:0;overflow:hidden;color:transparent;opacity:0;">Click to confirm your subscription. Link expires in 24 hours.</div>
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#0a0a0a;padding:40px 20px;">
<tr>
<td align="center">

<table cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:540px;">

<tr>
<td style="padding-bottom:20px;">
<span style="display:inline-block;padding:8px 14px;background:#c8ff00;color:#0a0a0a;border:2px solid #f5efe3;font-family:'Courier New',Consolas,monospace;font-size:14px;font-weight:700;letter-spacing:0.5px;border-radius:3px;">~/kaif</span>
</td>
</tr>

<tr>
<td style="background:#121212;border:3px solid #f5efe3;border-radius:4px;box-shadow:8px 8px 0 #c8ff00;padding:36px 28px;">

<span style="display:inline-block;padding:5px 12px;background:#c8ff00;color:#0a0a0a;border:2px solid #0a0a0a;font-family:'Courier New',Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:lowercase;border-radius:2px;">[ newsletter ]</span>

<h1 style="margin:20px 0 12px;font-family:Impact,'Arial Black','Helvetica Neue',sans-serif;font-size:40px;line-height:0.92;letter-spacing:-0.5px;color:#f5efe3;text-transform:uppercase;font-weight:400;">CONFIRM YOUR<br>SUBSCRIPTION</h1>

<p style="margin:0 0 28px;font-family:'Courier New',Consolas,monospace;font-size:14px;line-height:1.7;color:#a8a8a8;">You're one click away from build logs, new agents, and things I break at 2am.</p>

<table cellpadding="0" cellspacing="0" border="0">
<tr>
<td style="background:#0a0a0a;padding:0 4px 4px 0;">
<a href="{link}" style="display:inline-block;background:#c8ff00;color:#0a0a0a;padding:14px 28px;text-decoration:none;font-family:'Courier New',Consolas,monospace;font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;border:2px solid #0a0a0a;">CONFIRM &rarr;</a>
</td>
</tr>
</table>

<div style="margin-top:36px;padding-top:22px;border-top:2px solid #333333;">
<p style="margin:0 0 10px;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">LINK EXPIRES IN 24 HOURS</p>
<p style="margin:0;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">IF YOU DIDN'T REQUEST THIS, IGNORE THIS EMAIL</p>
</div>

</td>
</tr>

<tr>
<td style="padding-top:28px;text-align:center;">
<p style="margin:0 0 6px;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;line-height:1.6;letter-spacing:0.5px;">SENT BY KAIF ANSARI &middot; MUZAFFARNAGAR, INDIA</p>
<p style="margin:0;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;line-height:1.6;letter-spacing:0.5px;"><a href="{SITE_URL}" style="color:#c8ff00;text-decoration:none;border-bottom:1px dashed #c8ff00;">kaifansari.me</a></p>
</td>
</tr>

</table>

</td>
</tr>
</table>
</body>
</html>"""

    msg.set_content(plain)
    msg.add_alternative(html, subtype='html')

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Access-Control-Max-Age', '86400')
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            data = json.loads(self.rfile.read(length))
            email = (data.get('email') or '').strip().lower()
            token = data.get('token') or ''
            ip = get_client_ip(self)

            if '@' not in email or '.' not in email.split('@')[-1] or len(email) > 200:
                return self.json(400, {'success': False, 'error': 'invalid email'})

            if not UPSTASH_URL or not UPSTASH_TOKEN:
                return self.json(500, {'success': False, 'error': 'storage not configured'})

            if not verify_turnstile(token, ip):
                return self.json(400, {'success': False, 'error': 'captcha failed'})

            if not rate_limit(ip):
                return self.json(429, {'success': False, 'error': 'too many attempts'})

            exists = redis_cmd('exists', f'confirmed:{email}')
            if exists is None:
                return self.json(500, {'success': False, 'error': 'storage error'})
            try:
                if int(exists) > 0:
                    return self.json(200, {'success': True, 'message': 'already subscribed'})
            except (TypeError, ValueError):
                return self.json(500, {'success': False, 'error': 'storage error'})

            confirm_token = secrets.token_urlsafe(32)
            saved = redis_cmd('set', f'pending:{confirm_token}', email)
            if saved is None:
                return self.json(500, {'success': False, 'error': 'storage error'})
            redis_cmd('expire', f'pending:{confirm_token}', 86400)

            try:
                send_confirmation(email, confirm_token)
            except Exception:
                redis_cmd('del', f'pending:{confirm_token}')
                return self.json(500, {'success': False, 'error': 'failed to send email'})

            return self.json(200, {'success': True, 'message': 'confirmation sent'})
        except Exception as e:
            return self.json(500, {'success': False, 'error': str(e)})

    def json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())