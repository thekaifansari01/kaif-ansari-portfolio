import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import html as html_lib
import json
import secrets
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests

from session_lib import (
    SITE_URL, redis_cmd, get_client_ip, cors_origin,
    json_response, handle_options,
)
from mailer_lib import smtp_send

SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
TO_EMAIL = os.environ.get('TO_EMAIL', 'kaif.ansari.global@gmail.com')
CACHE_KEY = 'projects:cache'
CACHE_TTL = 60


def _verify_turnstile(token, ip):
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


def _send_contact_email(name, email, message):
    safe_name = html_lib.escape(name)
    safe_email = html_lib.escape(email)
    safe_message = html_lib.escape(message)
    subject = f'New Contact Form from {name}'
    text = (
        f"Name: {name}\n"
        f"Email: {email}\n\n"
        f"Message:\n{message}\n"
    )
    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;font-family:'Courier New',monospace;">
<div style="max-width:560px;margin:40px auto;background:#121212;border:3px solid #f5efe3;padding:32px;box-shadow:8px 8px 0 #c8ff00;">
<span style="display:inline-block;padding:5px 12px;background:#c8ff00;color:#0a0a0a;font-weight:700;font-size:11px;letter-spacing:1px;">[ contact ]</span>
<h1 style="margin:18px 0 12px;color:#f5efe3;font-family:Impact,sans-serif;font-size:28px;letter-spacing:-0.5px;text-transform:uppercase;font-weight:400;">New Message</h1>
<p style="color:#a8a8a8;font-size:13px;margin:0 0 4px;"><strong style="color:#c8ff00;">From:</strong> {safe_name}</p>
<p style="color:#a8a8a8;font-size:13px;margin:0 0 20px;"><strong style="color:#c8ff00;">Email:</strong> {safe_email}</p>
<div style="color:#e0e0e0;font-size:14px;line-height:1.75;white-space:pre-wrap;padding:16px;background:#0a0a0a;border-left:4px solid #c8ff00;margin:0 0 24px;">{safe_message}</div>
<p style="color:#6a6a6a;font-size:11px;margin:0;padding-top:18px;border-top:2px solid #333;">reply to this email to respond directly</p>
</div>
</body></html>"""
    try:
        smtp_send(TO_EMAIL, subject, text, html, reply_to=email)
        return True
    except Exception:
        return False


def _send_confirmation(email, token, unsub_token):
    link = f'{SITE_URL}/api/confirm?token={token}'
    unsub_link = f'{SITE_URL}/api/unsubscribe?token={unsub_token}'
    text = (
        'Confirm your subscription\n\n'
        "You're one click away from build logs, new agents, and things I break at 2am.\n\n"
        f'Confirm here:\n{link}\n\n'
        'Link expires in 24 hours.\n\n'
        "If you didn't request this, ignore this email.\n\n"
        f'Unsubscribe: {unsub_link}\n\n'
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
<p style="margin:0 0 10px;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">IF YOU DIDN'T REQUEST THIS, IGNORE THIS EMAIL</p>
<p style="margin:0;font-family:'Courier New',Consolas,monospace;font-size:11px;color:#6a6a6a;letter-spacing:1.5px;"><a href="{unsub_link}" style="color:#6a6a6a;text-decoration:underline;">UNSUBSCRIBE</a></p>
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


def _fetch_projects():
    cached = redis_cmd('get', CACHE_KEY)
    if cached:
        try:
            return json.loads(cached)
        except (TypeError, ValueError):
            pass

    raw = redis_cmd('hgetall', 'projects:list') or []
    projects = []
    if isinstance(raw, list):
        for i in range(0, len(raw), 2):
            try:
                projects.append(json.loads(raw[i + 1]))
            except (IndexError, TypeError, ValueError):
                pass

    projects.sort(key=lambda p: int(p.get('order') or 0))

    try:
        redis_cmd('set', CACHE_KEY, json.dumps(projects))
        redis_cmd('expire', CACHE_KEY, CACHE_TTL)
    except Exception:
        pass

    return projects


class handler(BaseHTTPRequestHandler):
    def _action(self):
        return (parse_qs(urlparse(self.path).query).get('action') or [''])[0].strip()

    def _body(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            if length <= 0:
                return {}
            return json.loads(self.rfile.read(length) or b'{}')
        except Exception:
            return {}

    def _redirect(self, url):
        self.send_response(302)
        self.send_header('Location', url)
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.end_headers()

    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        action = self._action()
        if action == 'confirm':
            return self._confirm()
        if action == 'unsubscribe':
            return self._unsubscribe()
        if action == 'projects':
            return self._projects()
        return json_response(self, 404, {'success': False, 'error': 'not found'})

    def do_POST(self):
        action = self._action()
        if action == 'send':
            return self._send()
        if action == 'subscribe':
            return self._subscribe()
        return json_response(self, 404, {'success': False, 'error': 'not found'})

    def _send(self):
        try:
            data = self._body()
            name = (data.get('name') or '').strip()
            email = (data.get('email') or '').strip().lower()
            message = (data.get('message') or '').strip()
            token = (data.get('token') or '').strip()
            ip = get_client_ip(self)

            if not name or not email or not message:
                return json_response(self, 400, {'success': False, 'error': 'All fields are required'})
            if '@' not in email or '.' not in email.split('@')[-1]:
                return json_response(self, 400, {'success': False, 'error': 'Invalid email address'})
            if len(name) > 100 or len(email) > 200 or len(message) > 5000:
                return json_response(self, 400, {'success': False, 'error': 'Input too long'})
            if not token:
                return json_response(self, 400, {'success': False, 'error': 'Missing CAPTCHA token'})

            if not _verify_turnstile(token, ip):
                return json_response(self, 400, {'success': False, 'error': 'CAPTCHA verification failed'})

            rl_key = f'rl:contact:{ip}'
            count = redis_cmd('incr', rl_key)
            try:
                count = int(count) if count is not None else 0
            except (TypeError, ValueError):
                count = 0
            if count == 1:
                redis_cmd('expire', rl_key, 3600)
            if count > 3:
                return json_response(self, 429, {'success': False, 'error': 'Too many attempts. Try again later.'})

            message_id = secrets.token_urlsafe(16)
            stored = False

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

            email_sent = _send_contact_email(name, email, message)

            if stored:
                try:
                    raw = redis_cmd('hget', 'contact:messages', message_id)
                    if raw:
                        p = json.loads(raw)
                        p['email_sent'] = bool(email_sent)
                        redis_cmd('hset', 'contact:messages', message_id, json.dumps(p))
                except Exception:
                    pass

            if email_sent:
                return json_response(self, 200, {'success': True, 'message': 'Message sent successfully!'})
            if stored:
                return json_response(self, 200, {'success': True, 'message': 'Message received. Delivery may be delayed.'})

            return json_response(self, 500, {'success': False, 'error': 'Failed to deliver message. Please try again.'})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _subscribe(self):
        try:
            data = self._body()
            email = (data.get('email') or '').strip().lower()
            token = data.get('token') or ''
            ip = get_client_ip(self)

            if '@' not in email or '.' not in email.split('@')[-1] or len(email) > 200:
                return json_response(self, 400, {'success': False, 'error': 'invalid email'})

            if not _verify_turnstile(token, ip):
                return json_response(self, 400, {'success': False, 'error': 'captcha failed'})

            rl_key = f'rl:nl:{ip}'
            count = redis_cmd('incr', rl_key)
            try:
                count = int(count) if count is not None else 0
            except (TypeError, ValueError):
                count = 0
            if count == 1:
                redis_cmd('expire', rl_key, 3600)
            if count > 5:
                return json_response(self, 429, {'success': False, 'error': 'too many attempts'})

            existing_raw = redis_cmd('hget', 'newsletter:subscribers', email)
            if existing_raw:
                try:
                    existing = json.loads(existing_raw)
                except (TypeError, ValueError):
                    existing = {}
                status = existing.get('status', '')
                if status == 'confirmed':
                    return json_response(self, 200, {'success': True, 'message': 'already subscribed'})
                if status == 'pending':
                    return json_response(self, 200, {'success': True, 'message': 'confirmation sent'})

            confirm_token = secrets.token_urlsafe(32)
            unsub_token = secrets.token_urlsafe(32)
            now = int(time.time())
            payload = {
                'status': 'pending',
                'token': confirm_token,
                'unsub_token': unsub_token,
                'subscribed_at': now,
                'confirmed_at': 0,
                'source': 'web',
                'ip': ip,
            }
            saved = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(payload))
            if saved is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            tok_ok = redis_cmd('set', f'newsletter:token:{confirm_token}', email)
            if tok_ok is None:
                redis_cmd('hdel', 'newsletter:subscribers', email)
                return json_response(self, 500, {'success': False, 'error': 'storage error'})
            redis_cmd('expire', f'newsletter:token:{confirm_token}', 86400)

            redis_cmd('set', f'newsletter:unsub_token:{unsub_token}', email)

            try:
                _send_confirmation(email, confirm_token, unsub_token)
            except Exception:
                redis_cmd('hdel', 'newsletter:subscribers', email)
                redis_cmd('del', f'newsletter:token:{confirm_token}')
                redis_cmd('del', f'newsletter:unsub_token:{unsub_token}')
                return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            return json_response(self, 200, {'success': True, 'message': 'confirmation sent'})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _confirm(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get('token') or [''])[0].strip()
            if not token or len(token) < 10:
                return self._redirect(f'{SITE_URL}/?subscribed=0')

            email = redis_cmd('get', f'newsletter:token:{token}')
            if not email:
                return self._redirect(f'{SITE_URL}/?subscribed=0')

            raw = redis_cmd('hget', 'newsletter:subscribers', email)
            if not raw:
                return self._redirect(f'{SITE_URL}/?subscribed=0')

            try:
                data = json.loads(raw)
            except (TypeError, ValueError):
                return self._redirect(f'{SITE_URL}/?subscribed=0')

            if data.get('status') == 'confirmed':
                redis_cmd('del', f'newsletter:token:{token}')
                return self._redirect(f'{SITE_URL}/?subscribed=1')

            data['status'] = 'confirmed'
            data['confirmed_at'] = int(time.time())
            data['token'] = ''
            ok = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(data))
            if ok is None:
                return self._redirect(f'{SITE_URL}/?subscribed=0')

            redis_cmd('del', f'newsletter:token:{token}')
            return self._redirect(f'{SITE_URL}/?subscribed=1')
        except Exception:
            return self._redirect(f'{SITE_URL}/?subscribed=0')

    def _unsubscribe(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get('token') or [''])[0].strip()

            if not token or len(token) < 10:
                return self._redirect(f'{SITE_URL}/?unsubscribed=0')

            email = redis_cmd('get', f'newsletter:unsub_token:{token}')
            if not email:
                return self._redirect(f'{SITE_URL}/?unsubscribed=0')

            raw = redis_cmd('hget', 'newsletter:subscribers', email)
            if not raw:
                return self._redirect(f'{SITE_URL}/?unsubscribed=0')

            try:
                data = json.loads(raw)
            except (TypeError, ValueError):
                return self._redirect(f'{SITE_URL}/?unsubscribed=0')

            if data.get('status') == 'unsubscribed':
                return self._redirect(f'{SITE_URL}/?unsubscribed=1')

            data['status'] = 'unsubscribed'
            old_tok = data.get('token') or ''
            if old_tok:
                redis_cmd('del', f'newsletter:token:{old_tok}')
            data['token'] = ''

            ok = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(data))
            if ok is None:
                return self._redirect(f'{SITE_URL}/?unsubscribed=0')

            return self._redirect(f'{SITE_URL}/?unsubscribed=1')
        except Exception:
            return self._redirect(f'{SITE_URL}/?unsubscribed=0')

    def _projects(self):
        try:
            projects = _fetch_projects()
            safe = []
            for p in projects:
                safe.append({
                    'id': p.get('id', ''),
                    'title': p.get('title', ''),
                    'category': p.get('category', ''),
                    'status': p.get('status', 'shipped'),
                    'description': p.get('description', ''),
                    'features': p.get('features', []) or [],
                    'stack': p.get('stack', []) or [],
                    'github_url': p.get('github_url', ''),
                    'live_url': p.get('live_url', ''),
                    'featured': bool(p.get('featured', False)),
                    'path': p.get('path', ''),
                    'metrics': p.get('metrics', {}) or {},
                })

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', cors_origin(self))
            self.send_header('Cache-Control', 'public, max-age=30')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'data': safe}).encode())
        except Exception:
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', cors_origin(self))
            self.end_headers()
            self.wfile.write(b'{"success":false,"error":"server error"}')