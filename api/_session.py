import json
import os
import time

import requests

UPSTASH_URL = os.environ.get('UPSTASH_REDIS_REST_URL')
UPSTASH_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN')
SITE_URL = os.environ.get('SITE_URL', 'https://kaifansari.me').rstrip('/')
ADMIN_EMAIL = (os.environ.get('ADMIN_EMAIL') or '').strip().lower()
SESSION_TTL = 7 * 24 * 60 * 60
COOKIE_NAME = 'admin_session'
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
            timeout=8,
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


def parse_cookies(handler):
    header = handler.headers.get('Cookie', '')
    cookies = {}
    for part in header.split(';'):
        part = part.strip()
        if not part or '=' not in part:
            continue
        k, v = part.split('=', 1)
        cookies[k.strip()] = v.strip()
    return cookies


def get_session(handler):
    sid = parse_cookies(handler).get(COOKIE_NAME)
    if not sid or len(sid) < 20:
        return None
    raw = redis_cmd('get', f'admin:session:{sid}')
    if not raw:
        return None
    try:
        data = json.loads(raw)
    except (TypeError, ValueError):
        return None
    if not data.get('email'):
        return None
    return {'sid': sid, 'email': data['email'], 'ip': data.get('ip', '')}


def session_cookie(sid, max_age):
    return f'{COOKIE_NAME}={sid}; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age={max_age}'


def clear_cookie():
    return f'{COOKIE_NAME}=; Path=/; HttpOnly; Secure; SameSite=Lax; Max-Age=0'


def audit(actor, action, target='', meta=None):
    try:
        entry = {
            'actor': actor,
            'action': action,
            'target': target,
            'meta': meta or {},
            'ts': int(time.time()),
        }
        redis_cmd('lpush', 'admin:audit', json.dumps(entry))
        redis_cmd('ltrim', 'admin:audit', '0', '999')
    except Exception:
        pass


def json_response(handler, status, payload, extra_headers=None):
    handler.send_response(status)
    handler.send_header('Content-Type', 'application/json')
    handler.send_header('Access-Control-Allow-Origin', cors_origin(handler))
    handler.send_header('Access-Control-Allow-Credentials', 'true')
    handler.send_header('Cache-Control', 'no-store')
    if extra_headers:
        for k, v in extra_headers.items():
            handler.send_header(k, v)
    handler.end_headers()
    handler.wfile.write(json.dumps(payload).encode())


def handle_options(handler):
    handler.send_response(200)
    handler.send_header('Access-Control-Allow-Origin', cors_origin(handler))
    handler.send_header('Access-Control-Allow-Methods', 'GET, POST, PATCH, DELETE, OPTIONS')
    handler.send_header('Access-Control-Allow-Headers', 'Content-Type')
    handler.send_header('Access-Control-Allow-Credentials', 'true')
    handler.send_header('Access-Control-Max-Age', '86400')
    handler.end_headers()


def scan_all(pattern):
    cursor = '0'
    keys = []
    for _ in range(50):
        result = redis_cmd('scan', cursor, 'match', pattern, 'count', '200')
        if not result or not isinstance(result, list) or len(result) < 2:
            break
        cursor = str(result[0])
        batch = result[1] or []
        keys.extend(batch)
        if cursor == '0':
            break
    return keys