import json
import secrets
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from _session import (
    SITE_URL, SESSION_TTL, redis_cmd, get_client_ip, audit, session_cookie,
)


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get('token') or [''])[0].strip()

            if not token or len(token) < 10:
                return self.fail()

            email = redis_cmd('get', f'admin:magic:{token}')
            if not email:
                return self.fail()

            redis_cmd('del', f'admin:magic:{token}')

            sid = secrets.token_urlsafe(32)
            payload = json.dumps({
                'email': email,
                'ip': get_client_ip(self),
                'created': int(time.time()),
            })
            ok = redis_cmd('set', f'admin:session:{sid}', payload)
            if ok is None:
                return self.fail()

            redis_cmd('expire', f'admin:session:{sid}', SESSION_TTL)
            audit(email, 'login_success', email, {'ip': get_client_ip(self)})

            self.send_response(302)
            self.send_header('Location', f'{SITE_URL}/admin')
            self.send_header('Set-Cookie', session_cookie(sid, SESSION_TTL))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
        except Exception:
            return self.fail()

    def fail(self):
        self.send_response(302)
        self.send_header('Location', f'{SITE_URL}/admin?error=login')
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()