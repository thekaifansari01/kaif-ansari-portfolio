import json
import secrets
from http.server import BaseHTTPRequestHandler

from _session import (
    ADMIN_EMAIL, SITE_URL, redis_cmd, get_client_ip, json_response,
    handle_options, audit,
)
from _mailer import smtp_send


def send_magic_email(email, token):
    link = f'{SITE_URL}/api/admin_verify?token={token}'
    text = (
        'Admin login\n\n'
        f'Click to sign in:\n{link}\n\n'
        'Link expires in 15 minutes.\n'
        "If you didn't request this, ignore this email.\n"
    )
    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;font-family:'Courier New',monospace;">
<div style="max-width:520px;margin:40px auto;background:#121212;border:3px solid #f5efe3;padding:32px;box-shadow:8px 8px 0 #c8ff00;">
<span style="display:inline-block;padding:5px 12px;background:#c8ff00;color:#0a0a0a;font-weight:700;font-size:11px;letter-spacing:1px;">[ admin ]</span>
<h1 style="margin:18px 0 12px;color:#f5efe3;font-family:Impact,sans-serif;font-size:32px;letter-spacing:-0.5px;text-transform:uppercase;font-weight:400;">Sign in to<br>admin panel</h1>
<p style="color:#a8a8a8;font-size:13px;line-height:1.7;margin:0 0 24px;">Click the button below. Link expires in 15 minutes.</p>
<a href="{link}" style="display:inline-block;background:#c8ff00;color:#0a0a0a;padding:12px 26px;text-decoration:none;font-weight:700;font-size:13px;letter-spacing:1px;text-transform:uppercase;border:2px solid #0a0a0a;">SIGN IN &rarr;</a>
<p style="color:#6a6a6a;font-size:11px;margin:28px 0 0;padding-top:18px;border-top:2px solid #333;">IF YOU DIDN'T REQUEST THIS, IGNORE THIS EMAIL</p>
</div>
</body></html>"""
    smtp_send(email, 'Admin login - kaif ansari', text, html)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
        try:
            length = int(self.headers.get('Content-Length', 0))
            raw = self.rfile.read(length) if length else b'{}'
            body = json.loads(raw)
            email = (body.get('email') or '').strip().lower()
            ip = get_client_ip(self)

            if not email or '@' not in email or len(email) > 200:
                return json_response(self, 400, {'success': False, 'error': 'invalid email'})

            if not ADMIN_EMAIL:
                return json_response(self, 500, {'success': False, 'error': 'admin not configured'})

            rl_key = f'rl:admin-login:{ip}'
            count = redis_cmd('incr', rl_key)
            try:
                count = int(count) if count is not None else 0
            except (TypeError, ValueError):
                count = 0
            if count == 1:
                redis_cmd('expire', rl_key, 900)
            if count > 5:
                return json_response(self, 429, {'success': False, 'error': 'too many attempts, try again later'})

            if email != ADMIN_EMAIL:
                audit('system', 'login_attempt_unknown', email, {'ip': ip})
                return json_response(self, 200, {'success': True, 'message': 'if that email is registered, a link is on its way'})

            token = secrets.token_urlsafe(32)
            saved = redis_cmd('set', f'admin:magic:{token}', email)
            if saved is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})
            redis_cmd('expire', f'admin:magic:{token}', 900)

            try:
                send_magic_email(email, token)
            except Exception:
                redis_cmd('del', f'admin:magic:{token}')
                return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            audit('system', 'login_link_sent', email, {'ip': ip})
            return json_response(self, 200, {'success': True, 'message': 'if that email is registered, a link is on its way'})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})