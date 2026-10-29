import json
import os
from http.server import BaseHTTPRequestHandler

import requests

UPSTASH_URL = os.environ.get('UPSTASH_REDIS_REST_URL')
UPSTASH_TOKEN = os.environ.get('UPSTASH_REDIS_REST_TOKEN')
SITE_URL = os.environ.get('SITE_URL', 'https://kaifansari.me').rstrip('/')
ALLOWED_ORIGINS = [o.strip() for o in os.environ.get('ALLOWED_ORIGINS', SITE_URL).split(',') if o.strip()]
CACHE_KEY = 'projects:cache'
CACHE_TTL = 60


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


def cors_origin(handler):
    origin = handler.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        return origin
    return ALLOWED_ORIGINS[0] if ALLOWED_ORIGINS else SITE_URL


def fetch_projects():
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
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.end_headers()

    def do_GET(self):
        try:
            projects = fetch_projects()
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