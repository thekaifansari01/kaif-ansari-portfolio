import json
import os
import secrets
import time

import requests
import smtplib
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler

SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
TO_EMAIL = os.environ.get('TO_EMAIL', 'kaif.ansari.global@gmail.com')
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


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

    def do_POST(self):
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)

            name = (data.get('name') or '').strip()
            email = (data.get('email') or '').strip().lower()
            message = (data.get('message') or '').strip()
            token = (data.get('token') or '').strip()
            ip = get_client_ip(self)

            if not name or not email or not message:
                return self.send_json_response(400, {'success': False, 'error': 'All fields are required'})
            if '@' not in email or '.' not in email.split('@')[-1]:
                return self.send_json_response(400, {'success': False, 'error': 'Invalid email address'})
            if len(name) > 100 or len(email) > 200 or len(message) > 5000:
                return self.send_json_response(400, {'success': False, 'error': 'Input too long'})
            if not token:
                return self.send_json_response(400, {'success': False, 'error': 'Missing CAPTCHA token'})

            try:
                verify = requests.post(
                    'https://challenges.cloudflare.com/turnstile/v0/siteverify',
                    data={'secret': SECRET_KEY, 'response': token, 'remoteip': ip},
                    timeout=5,
                ).json()
            except Exception:
                return self.send_json_response(500, {'success': False, 'error': 'Captcha verification failed'})
            if not verify.get('success'):
                return self.send_json_response(400, {'success': False, 'error': 'CAPTCHA verification failed'})

            if UPSTASH_URL and UPSTASH_TOKEN:
                rl_key = f'rl:contact:{ip}'
                count = redis_cmd('incr', rl_key)
                try:
                    count = int(count) if count is not None else 0
                except (TypeError, ValueError):
                    count = 0
                if count == 1:
                    redis_cmd('expire', rl_key, 3600)
                if count > 3:
                    return self.send_json_response(429, {'success': False, 'error': 'Too many attempts. Try again later.'})

            message_id = secrets.token_urlsafe(16)
            stored = False

            if UPSTASH_URL and UPSTASH_TOKEN:
                payload = {
                    'name': name,
                    'email': email,
                    'message': message,
                    'ip': ip,
                    'status': 'unread',
                    'created_at': int(time.time()),
                }
                result = redis_cmd('hset', 'contact:messages', message_id, json.dumps(payload))
                if result is not None:
                    redis_cmd('lpush', 'contact:order', message_id)
                    redis_cmd('sadd', 'contact:unread', message_id)
                    stored = True

            email_sent = self.send_email(name, email, message)

            if stored:
                new_status = 'read' if email_sent else 'unread'
                try:
                    raw = redis_cmd('hget', 'contact:messages', message_id)
                    if raw:
                        p = json.loads(raw)
                        p['status'] = new_status
                        p['email_sent'] = bool(email_sent)
                        redis_cmd('hset', 'contact:messages', message_id, json.dumps(p))
                        if new_status == 'read':
                            redis_cmd('srem', 'contact:unread', message_id)
                except Exception:
                    pass

            if email_sent:
                return self.send_json_response(200, {'success': True, 'message': 'Message sent successfully!'})
            if stored:
                return self.send_json_response(200, {'success': True, 'message': 'Message received. Delivery may be delayed.'})

            return self.send_json_response(500, {'success': False, 'error': 'Failed to deliver message. Please try again.'})

        except Exception as e:
            print(f'Error: {e}')
            return self.send_json_response(500, {'success': False, 'error': 'Internal server error'})

    def send_email(self, name, email, message):
        if not SMTP_USER or not SMTP_PASS:
            return False
        try:
            msg = EmailMessage()
            msg.set_content(
                f"Name: {name}\n"
                f"Email: {email}\n\n"
                f"Message:\n{message}\n"
            )
            msg['Subject'] = f'New Contact Form from {name}'
            msg['From'] = SMTP_USER
            msg['To'] = TO_EMAIL
            msg['Reply-To'] = email
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            return True
        except Exception as e:
            print(f'SMTP Error: {e}')
            return False

    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())