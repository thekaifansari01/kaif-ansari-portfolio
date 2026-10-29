import io
import json
import time
from csv import writer as csv_writer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from session_lib import (
    get_session, json_response, handle_options, redis_cmd, audit, SITE_URL,
)
from mailer_lib import smtp_send


def parse_subs(raw):
    result = []
    if not isinstance(raw, list):
        return result
    for i in range(0, len(raw), 2):
        try:
            email = raw[i]
            data = json.loads(raw[i + 1])
            data['email'] = email
            result.append(data)
        except (IndexError, TypeError, ValueError):
            pass
    return result


def send_confirmation_email(email, token):
    link = f'{SITE_URL}/api/confirm?token={token}'
    text = (
        'Confirm your subscription\n\n'
        f'Confirm here:\n{link}\n\n'
        'Link expires in 24 hours.\n'
    )
    smtp_send(email, 'Confirm your subscription - kaif ansari', text)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        qs = parse_qs(urlparse(self.path).query)
        status_filter = (qs.get('status') or ['all'])[0]
        format_type = (qs.get('format') or ['json'])[0]
        try:
            page = max(0, int((qs.get('page') or ['0'])[0]))
        except (TypeError, ValueError):
            page = 0
        try:
            per_page = min(200, max(1, int((qs.get('per_page') or ['25'])[0])))
        except (TypeError, ValueError):
            per_page = 25

        subs = parse_subs(redis_cmd('hgetall', 'newsletter:subscribers') or [])

        if status_filter and status_filter != 'all':
            subs = [s for s in subs if s.get('status') == status_filter]

        subs.sort(key=lambda s: int(s.get('subscribed_at') or 0), reverse=True)
        total = len(subs)

        if format_type == 'csv':
            buf = io.StringIO()
            w = csv_writer(buf)
            w.writerow(['email', 'status', 'subscribed_at', 'confirmed_at', 'source', 'ip'])
            for s in subs:
                w.writerow([
                    s.get('email', ''),
                    s.get('status', ''),
                    s.get('subscribed_at', ''),
                    s.get('confirmed_at', ''),
                    s.get('source', ''),
                    s.get('ip', ''),
                ])
            body = buf.getvalue().encode()
            self.send_response(200)
            self.send_header('Content-Type', 'text/csv; charset=utf-8')
            self.send_header('Content-Disposition', 'attachment; filename="subscribers.csv"')
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
            self.wfile.write(body)
            return

        start = page * per_page
        end = start + per_page
        paginated = subs[start:end]

        return json_response(self, 200, {
            'success': True,
            'data': paginated,
            'total': total,
            'page': page,
            'per_page': per_page,
        })

    def do_POST(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            email = (body.get('email') or '').strip().lower()
            status = (body.get('status') or 'confirmed').strip()

            if not email or '@' not in email or '.' not in email.split('@')[-1] or len(email) > 200:
                return json_response(self, 400, {'success': False, 'error': 'invalid email'})
            if status not in ('pending', 'confirmed'):
                return json_response(self, 400, {'success': False, 'error': 'invalid status'})

            existing = redis_cmd('hget', 'newsletter:subscribers', email)
            if existing:
                return json_response(self, 409, {'success': False, 'error': 'subscriber already exists'})

            token = ''
            now = int(time.time())
            if status == 'pending':
                import secrets
                token = secrets.token_urlsafe(32)

            payload = {
                'status': status,
                'token': token,
                'subscribed_at': now,
                'confirmed_at': now if status == 'confirmed' else 0,
                'source': 'admin',
                'ip': '',
            }
            ok = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(payload))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            if status == 'pending' and token:
                redis_cmd('set', f'newsletter:token:{token}', email)
                redis_cmd('expire', f'newsletter:token:{token}', 86400)
                try:
                    send_confirmation_email(email, token)
                except Exception:
                    redis_cmd('hdel', 'newsletter:subscribers', email)
                    redis_cmd('del', f'newsletter:token:{token}')
                    return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            audit(sess['email'], 'subscriber_add', email, {'status': status})
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def do_PATCH(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
            email = (body.get('email') or '').strip().lower()
            action = (body.get('action') or '').strip()

            if not email or action not in ('confirm', 'unsubscribe', 'pending', 'resend'):
                return json_response(self, 400, {'success': False, 'error': 'invalid request'})

            raw = redis_cmd('hget', 'newsletter:subscribers', email)
            if not raw:
                return json_response(self, 404, {'success': False, 'error': 'subscriber not found'})

            try:
                data = json.loads(raw)
            except (TypeError, ValueError):
                return json_response(self, 500, {'success': False, 'error': 'corrupt data'})

            now = int(time.time())

            if action == 'confirm':
                data['status'] = 'confirmed'
                data['confirmed_at'] = now
                old_token = data.get('token') or ''
                if old_token:
                    redis_cmd('del', f'newsletter:token:{old_token}')
                data['token'] = ''

            elif action == 'unsubscribe':
                data['status'] = 'unsubscribed'
                old_token = data.get('token') or ''
                if old_token:
                    redis_cmd('del', f'newsletter:token:{old_token}')
                data['token'] = ''

            elif action == 'pending':
                import secrets
                old_token = data.get('token') or ''
                if old_token:
                    redis_cmd('del', f'newsletter:token:{old_token}')
                new_token = secrets.token_urlsafe(32)
                data['status'] = 'pending'
                data['token'] = new_token
                redis_cmd('set', f'newsletter:token:{new_token}', email)
                redis_cmd('expire', f'newsletter:token:{new_token}', 86400)

            elif action == 'resend':
                if data.get('status') == 'confirmed':
                    return json_response(self, 400, {'success': False, 'error': 'already confirmed'})
                import secrets
                old_token = data.get('token') or ''
                if old_token:
                    redis_cmd('del', f'newsletter:token:{old_token}')
                new_token = secrets.token_urlsafe(32)
                data['token'] = new_token
                data['status'] = 'pending'
                redis_cmd('set', f'newsletter:token:{new_token}', email)
                redis_cmd('expire', f'newsletter:token:{new_token}', 86400)
                try:
                    send_confirmation_email(email, new_token)
                except Exception:
                    return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            ok = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(data))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            audit(sess['email'], f'subscriber_{action}', email)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def do_DELETE(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            qs = parse_qs(urlparse(self.path).query)
            email = (qs.get('email') or [''])[0].strip().lower()
            if not email:
                return json_response(self, 400, {'success': False, 'error': 'email required'})

            raw = redis_cmd('hget', 'newsletter:subscribers', email)
            if raw:
                try:
                    data = json.loads(raw)
                    tok = data.get('token') or ''
                    if tok:
                        redis_cmd('del', f'newsletter:token:{tok}')
                except (TypeError, ValueError):
                    pass

            ok = redis_cmd('hdel', 'newsletter:subscribers', email)
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            audit(sess['email'], 'subscriber_delete', email)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})