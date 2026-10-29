import json
import os
import secrets
import time

import requests
from http.server import BaseHTTPRequestHandler

from mailer_lib import smtp_send

SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
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
            timeout=6,
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


def send_confirmation(email, token):
    link = f'{SITE_URL}/api/confirm?token={token}'
    text = (
        'Confirm your subscription\n\n'
        "You're one click away from build logs, new agents, and things I break at 2am.\n\n"
        f'Confirm here:\n{link}\n\n'
        'Link expires in 24 hours.\n\n'
        "If you didn't request this, ignore this email.\n\n"
        f'~/\nkaif\n{SITE_URL}\n'
    )
    html = f"""<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><title>Confirm your subscription</title></head>
<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,Helvetica,sans-serif;">
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="background:#0a0a0a;padding:40px 20px;">
<tr><td align="center">
<table cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width:540px;">
<tr><td style="padding-bottom:20px;"><span style="display:inline-block;padding:8px 14px;background:#c8ff00;color:#0a0a0a;border:2px solid #f5efe3;font-family:'Courier New',Consolas,monospace;font-size:14px;font-weight:700;letter-spacing:0.5px;border-radius:3px;">~/kaif</span></td></tr>
<tr><td style="background:#121212;border:3px solid #f5efe3;border-radius:4px;box-shadow:8px 8px 0 #c8ff00;padding:36px 28px;">
<span style="display:inline-block;padding:5px 12px;background:#c8ff00;color:#0a0a0a;border:2px solid #0a0a0a;font-family:'Courier New',Consolas,monospace;font-size:11px;font-weight:700;letter-spacing:1px;text-transform:lowercase;border-radius:2px;">[ newsletter ]</span>
<h1 style="margin:20px 0 12px;font-family:Impact,'Arial Black',sans-serif;font-size:40px;line-height:0.92;color:#f5efe3;text-transform:uppercase;font-weight:400;">CONFIRM YOUR<br>SUBSCRIPTION</h1>
<p style="margin:0 0 28px;font-family:'Courier New',Consolas,monospace;font-size:14px;line-height:1.7;color:#a8a8a8;">You're one click away from build logs, new agents, and things I break at 2am.</p>
<a href="{link}" style="display:inline-block;background:#c8ff00;color:#0a0a0a;padding:14px 28px;text-decoration:none;font-family:'Courier New',Consolas,monospace;font-size:13px;font-weight:700;letter-spacing:1px;text-transform:uppercase;border:2px solid #0a0a0a;">CONFIRM &rarr;</a>
<div style="margin-top:36px;padding-top:22px;border-top:2px solid #333;">
<p style="margin:0 0 10px;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">LINK EXPIRES IN 24 HOURS</p>
<p style="margin:0;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">IF YOU DIDN'T REQUEST THIS, IGNORE THIS EMAIL</p>
</div>
</td></tr>
<tr><td style="padding-top:28px;text-align:center;">
<p style="margin:0 0 6px;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;">SENT BY KAIF ANSARI &middot; MUZAFFARNAGAR, INDIA</p>
<p style="margin:0;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;"><a href="{SITE_URL}" style="color:#c8ff00;text-decoration:none;border-bottom:1px dashed #c8ff00;">kaifansari.me</a></p>
</td></tr>
</table>
</td></tr>
</table>
</body></html>"""
    smtp_send(email, 'Confirm your subscription - kaif ansari', text, html)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
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

            rl_key = f'rl:nl:{ip}'
            count = redis_cmd('incr', rl_key)
            try:
                count = int(count) if count is not None else 0
            except (TypeError, ValueError):
                count = 0
            if count == 1:
                redis_cmd('expire', rl_key, 3600)
            if count > 5:
                return self.json(429, {'success': False, 'error': 'too many attempts'})

            existing_raw = redis_cmd('hget', 'newsletter:subscribers', email)
            if existing_raw:
                try:
                    existing = json.loads(existing_raw)
                except (TypeError, ValueError):
                    existing = {}
                status = existing.get('status', '')
                if status == 'confirmed':
                    return self.json(200, {'success': True, 'message': 'already subscribed'})
                if status == 'pending':
                    return self.json(200, {'success': True, 'message': 'confirmation sent'})

            confirm_token = secrets.token_urlsafe(32)
            now = int(time.time())
            payload = {
                'status': 'pending',
                'token': confirm_token,
                'subscribed_at': now,
                'confirmed_at': 0,
                'source': 'web',
                'ip': ip,
            }
            saved = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(payload))
            if saved is None:
                return self.json(500, {'success': False, 'error': 'storage error'})

            tok_ok = redis_cmd('set', f'newsletter:token:{confirm_token}', email)
            if tok_ok is None:
                redis_cmd('hdel', 'newsletter:subscribers', email)
                return self.json(500, {'success': False, 'error': 'storage error'})
            redis_cmd('expire', f'newsletter:token:{confirm_token}', 86400)

            try:
                send_confirmation(email, confirm_token)
            except Exception:
                redis_cmd('hdel', 'newsletter:subscribers', email)
                redis_cmd('del', f'newsletter:token:{confirm_token}')
                return self.json(500, {'success': False, 'error': 'failed to send email'})

            return self.json(200, {'success': True, 'message': 'confirmation sent'})
        except Exception:
            return self.json(500, {'success': False, 'error': 'server error'})

    def json(self, status, payload):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())