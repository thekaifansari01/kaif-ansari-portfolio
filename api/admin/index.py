import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import io
import json
import re
import secrets
import time
from csv import writer as csv_writer
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests

from session_lib import (
    ADMIN_EMAIL, SITE_URL, SESSION_TTL, COOKIE_NAME,
    redis_cmd, get_client_ip, cors_origin, get_session,
    session_cookie, clear_cookie, audit, json_response,
    handle_options, scan_all,
)
from mailer_lib import smtp_send


VALID_PROJECT_STATUS = ('live', 'shipped', 'wip')


def _send_magic_email(email, token):
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


def _send_confirmation_email(email, token, unsub_token):
    link = f'{SITE_URL}/api/confirm?token={token}'
    unsub_link = f'{SITE_URL}/api/unsubscribe?token={unsub_token}'
    text = (
        'Confirm your subscription\n\n'
        f'Confirm here:\n{link}\n\n'
        'Link expires in 24 hours.\n\n'
        f'Unsubscribe: {unsub_link}\n'
    )
    smtp_send(email, 'Confirm your subscription - kaif ansari', text)


def _reply_email(to_email, name, reply_text, admin_email):
    subject = 'Re: your message to kaif ansari'
    plain = f"Hi {name},\n\n{reply_text}\n\n—\nkaif\n{SITE_URL}\n"
    html = f"""<!DOCTYPE html>
<html><body style="margin:0;padding:0;background:#0a0a0a;font-family:'Courier New',monospace;">
<div style="max-width:560px;margin:40px auto;background:#121212;border:3px solid #f5efe3;padding:32px;box-shadow:8px 8px 0 #c8ff00;">
<span style="display:inline-block;padding:5px 12px;background:#c8ff00;color:#0a0a0a;font-weight:700;font-size:11px;letter-spacing:1px;">[ reply ]</span>
<h1 style="margin:18px 0 12px;color:#f5efe3;font-family:Impact,sans-serif;font-size:28px;letter-spacing:-0.5px;text-transform:uppercase;font-weight:400;">Hi {name}</h1>
<div style="color:#e0e0e0;font-size:14px;line-height:1.75;white-space:pre-wrap;margin:0 0 24px;">{reply_text}</div>
<p style="color:#6a6a6a;font-size:11px;margin:28px 0 0;padding-top:18px;border-top:2px solid #333;">— kaif · <a href="{SITE_URL}" style="color:#c8ff00;text-decoration:none;">kaifansari.me</a></p>
</div>
</body></html>"""
    smtp_send(to_email, subject, plain, html, reply_to=admin_email)


def _parse_subs(raw):
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


def _parse_projects(raw):
    projects = []
    if not isinstance(raw, list):
        return projects
    for i in range(0, len(raw), 2):
        try:
            projects.append(json.loads(raw[i + 1]))
        except (IndexError, TypeError, ValueError):
            pass
    return projects


def _validate_project(body):
    title = (body.get('title') or '').strip()
    category = (body.get('category') or '').strip()
    status = (body.get('status') or '').strip()
    description = (body.get('description') or '').strip()
    path = (body.get('path') or '').strip()
    features = body.get('features') or []
    stack = body.get('stack') or []
    github_url = (body.get('github_url') or '').strip()
    live_url = (body.get('live_url') or '').strip()
    featured = bool(body.get('featured', False))

    if not title or len(title) > 200:
        return None, 'title required (max 200)'
    if not category or len(category) > 100:
        return None, 'category required (max 100)'
    if status not in VALID_PROJECT_STATUS:
        return None, 'invalid status'
    if not description or len(description) > 2000:
        return None, 'description required (max 2000)'
    if not isinstance(features, list) or len(features) > 20:
        return None, 'features must be list (max 20)'
    if not isinstance(stack, list) or len(stack) > 30:
        return None, 'stack must be list (max 30)'

    features = [str(f)[:200] for f in features if f]
    stack = [str(s)[:50] for s in stack if s]

    return {
        'title': title,
        'category': category,
        'status': status,
        'description': description,
        'features': features,
        'stack': stack,
        'github_url': github_url[:500],
        'live_url': live_url[:500],
        'featured': featured,
        'path': path[:100],
    }, None


def _extract_owner_repo(url):
    if not url:
        return None, None
    m = re.match(r'https?://github\.com/([^/]+)/([^/?#]+)', url)
    if not m:
        return None, None
    return m.group(1), m.group(2).rstrip('/').replace('.git', '')


def _load_messages():
    raw = redis_cmd('hgetall', 'contact:messages') or []
    result = {}
    if isinstance(raw, list):
        for i in range(0, len(raw), 2):
            try:
                mid = raw[i]
                data = json.loads(raw[i + 1])
                data['id'] = mid
                result[mid] = data
            except (IndexError, TypeError, ValueError):
                pass
    return result


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
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()

    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        action = self._action()
        if action == 'verify':
            return self._verify()
        if action == 'me':
            return self._me()
        if action == 'dashboard':
            return self._dashboard()
        if action == 'subscribers':
            return self._subscribers_get()
        if action == 'messages':
            return self._messages_get()
        if action == 'projects':
            return self._projects_get()
        return json_response(self, 404, {'success': False, 'error': 'not found'})

    def do_POST(self):
        action = self._action()
        if action == 'login':
            return self._login()
        if action == 'logout':
            return self._logout()
        if action == 'migrate':
            return self._migrate()
        if action == 'subscribers':
            return self._subscribers_post()
        if action == 'messages':
            return self._messages_post()
        if action == 'projects':
            return self._projects_post()
        if action == 'projects_sync':
            return self._projects_sync()
        return json_response(self, 404, {'success': False, 'error': 'not found'})

    def do_PATCH(self):
        action = self._action()
        if action == 'subscribers':
            return self._subscribers_patch()
        if action == 'messages':
            return self._messages_patch()
        if action == 'projects':
            return self._projects_patch()
        return json_response(self, 404, {'success': False, 'error': 'not found'})

    def do_DELETE(self):
        action = self._action()
        if action == 'subscribers':
            return self._subscribers_delete()
        if action == 'messages':
            return self._messages_delete()
        if action == 'projects':
            return self._projects_delete()
        return json_response(self, 404, {'success': False, 'error': 'not found'})

    def _login(self):
        try:
            body = self._body()
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
                _send_magic_email(email, token)
            except Exception:
                redis_cmd('del', f'admin:magic:{token}')
                return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            audit('system', 'login_link_sent', email, {'ip': ip})
            return json_response(self, 200, {'success': True, 'message': 'if that email is registered, a link is on its way'})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _verify(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get('token') or [''])[0].strip()

            if not token or len(token) < 10:
                return self._redirect(f'{SITE_URL}/admin?error=login')

            email = redis_cmd('get', f'admin:magic:{token}')
            if not email:
                return self._redirect(f'{SITE_URL}/admin?error=login')

            redis_cmd('del', f'admin:magic:{token}')

            sid = secrets.token_urlsafe(32)
            payload = json.dumps({
                'email': email,
                'ip': get_client_ip(self),
                'created': int(time.time()),
            })
            ok = redis_cmd('set', f'admin:session:{sid}', payload)
            if ok is None:
                return self._redirect(f'{SITE_URL}/admin?error=login')

            redis_cmd('expire', f'admin:session:{sid}', SESSION_TTL)
            audit(email, 'login_success', email, {'ip': get_client_ip(self)})

            self.send_response(302)
            self.send_header('Location', f'{SITE_URL}/admin')
            self.send_header('Set-Cookie', session_cookie(sid, SESSION_TTL))
            self.send_header('Cache-Control', 'no-store')
            self.end_headers()
        except Exception:
            self._redirect(f'{SITE_URL}/admin?error=login')

    def _logout(self):
        sess = get_session(self)
        if sess:
            redis_cmd('del', f'admin:session:{sess["sid"]}')
            audit(sess['email'], 'logout', sess['email'])
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', cors_origin(self))
        self.send_header('Access-Control-Allow-Credentials', 'true')
        self.send_header('Set-Cookie', clear_cookie())
        self.end_headers()
        self.wfile.write(b'{"success":true}')

    def _me(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})
        return json_response(self, 200, {'success': True, 'email': sess['email']})

    def _dashboard(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        confirmed = 0
        pending = 0
        unsubscribed = 0

        subs_raw = redis_cmd('hgetall', 'newsletter:subscribers') or []
        if isinstance(subs_raw, list):
            for i in range(0, len(subs_raw), 2):
                try:
                    data = json.loads(subs_raw[i + 1])
                    status = data.get('status', '')
                    if status == 'confirmed':
                        confirmed += 1
                    elif status == 'pending':
                        pending += 1
                    elif status == 'unsubscribed':
                        unsubscribed += 1
                except (IndexError, TypeError, ValueError):
                    pass

        try:
            messages_total = int(redis_cmd('hlen', 'contact:messages') or 0)
        except (TypeError, ValueError):
            messages_total = 0

        try:
            messages_unread = int(redis_cmd('scard', 'contact:unread') or 0)
        except (TypeError, ValueError):
            messages_unread = 0

        try:
            migrated = bool(redis_cmd('exists', 'newsletter:migrated'))
        except Exception:
            migrated = False

        recent = []
        try:
            audit_raw = redis_cmd('lrange', 'admin:audit', '0', '9') or []
            for row in audit_raw:
                try:
                    recent.append(json.loads(row))
                except (TypeError, ValueError):
                    pass
        except Exception:
            pass

        return json_response(self, 200, {
            'success': True,
            'stats': {
                'confirmed': confirmed,
                'pending': pending,
                'unsubscribed': unsubscribed,
                'messages_total': messages_total,
                'messages_unread': messages_unread,
            },
            'migrated': migrated,
            'recent': recent,
            'ts': int(time.time()),
        })

    def _migrate(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        if redis_cmd('exists', 'newsletter:migrated'):
            return json_response(self, 200, {'success': True, 'message': 'already migrated', 'confirmed': 0, 'pending': 0})

        confirmed_keys = scan_all('confirmed:*')
        pending_keys = scan_all('pending:*')

        confirmed_added = 0
        pending_added = 0
        now = int(time.time())

        existing_fields = redis_cmd('hkeys', 'newsletter:subscribers') or []
        existing_set = set(existing_fields if isinstance(existing_fields, list) else [])

        for key in confirmed_keys:
            email = key[len('confirmed:'):] if key.startswith('confirmed:') else ''
            if not email or '@' not in email:
                continue
            if email in existing_set:
                continue
            payload = {
                'status': 'confirmed',
                'token': '',
                'subscribed_at': now,
                'confirmed_at': now,
                'source': 'legacy',
                'ip': '',
            }
            redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(payload))
            existing_set.add(email)
            confirmed_added += 1

        for key in pending_keys:
            if not key.startswith('pending:'):
                continue
            token = key[len('pending:'):]
            email = redis_cmd('get', key)
            if not email or '@' not in email:
                continue
            if email in existing_set:
                continue
            payload = {
                'status': 'pending',
                'token': token,
                'subscribed_at': now,
                'confirmed_at': 0,
                'source': 'legacy',
                'ip': '',
            }
            redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(payload))
            redis_cmd('set', f'newsletter:token:{token}', email)
            redis_cmd('expire', f'newsletter:token:{token}', 86400)
            existing_set.add(email)
            pending_added += 1

        redis_cmd('set', 'newsletter:migrated', str(now))
        audit(sess['email'], 'migrate', 'newsletter', {
            'confirmed': confirmed_added,
            'pending': pending_added,
        })

        return json_response(self, 200, {
            'success': True,
            'confirmed': confirmed_added,
            'pending': pending_added,
        })

    def _subscribers_get(self):
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

        subs = _parse_subs(redis_cmd('hgetall', 'newsletter:subscribers') or [])

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
        paginated = subs[start:start + per_page]

        return json_response(self, 200, {
            'success': True,
            'data': paginated,
            'total': total,
            'page': page,
            'per_page': per_page,
        })

    def _subscribers_post(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            body = self._body()
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
            unsub_token = secrets.token_urlsafe(32)
            now = int(time.time())
            if status == 'pending':
                token = secrets.token_urlsafe(32)

            payload = {
                'status': status,
                'token': token,
                'unsub_token': unsub_token,
                'subscribed_at': now,
                'confirmed_at': now if status == 'confirmed' else 0,
                'source': 'admin',
                'ip': '',
            }
            ok = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(payload))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            redis_cmd('set', f'newsletter:unsub_token:{unsub_token}', email)

            if status == 'pending' and token:
                redis_cmd('set', f'newsletter:token:{token}', email)
                redis_cmd('expire', f'newsletter:token:{token}', 86400)
                try:
                    _send_confirmation_email(email, token, unsub_token)
                except Exception:
                    redis_cmd('hdel', 'newsletter:subscribers', email)
                    redis_cmd('del', f'newsletter:token:{token}')
                    redis_cmd('del', f'newsletter:unsub_token:{unsub_token}')
                    return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            audit(sess['email'], 'subscriber_add', email, {'status': status})
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _subscribers_patch(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            body = self._body()
            email = (body.get('email') or '').strip().lower()
            action = (body.get('action') or '').strip()

            if action == 'backfill_unsub':
                count = 0
                subs_raw = redis_cmd('hgetall', 'newsletter:subscribers') or []
                if isinstance(subs_raw, list):
                    for i in range(0, len(subs_raw), 2):
                        try:
                            em = subs_raw[i]
                            data = json.loads(subs_raw[i + 1])
                            if not data.get('unsub_token'):
                                tok = secrets.token_urlsafe(32)
                                data['unsub_token'] = tok
                                redis_cmd('hset', 'newsletter:subscribers', em, json.dumps(data))
                                redis_cmd('set', f'newsletter:unsub_token:{tok}', em)
                                count += 1
                            else:
                                redis_cmd('set', f'newsletter:unsub_token:{data["unsub_token"]}', em)
                        except (IndexError, TypeError, ValueError):
                            continue
                audit(sess['email'], 'backfill_unsub', '', {'count': count})
                return json_response(self, 200, {'success': True, 'count': count})

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
                old_token = data.get('token') or ''
                if old_token:
                    redis_cmd('del', f'newsletter:token:{old_token}')
                new_token = secrets.token_urlsafe(32)
                data['token'] = new_token
                data['status'] = 'pending'
                redis_cmd('set', f'newsletter:token:{new_token}', email)
                redis_cmd('expire', f'newsletter:token:{new_token}', 86400)
                unsub_tok = data.get('unsub_token') or ''
                try:
                    _send_confirmation_email(email, new_token, unsub_tok)
                except Exception:
                    return json_response(self, 500, {'success': False, 'error': 'failed to send email'})

            ok = redis_cmd('hset', 'newsletter:subscribers', email, json.dumps(data))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            audit(sess['email'], f'subscriber_{action}', email)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _subscribers_delete(self):
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
                    unsub_tok = data.get('unsub_token') or ''
                    if unsub_tok:
                        redis_cmd('del', f'newsletter:unsub_token:{unsub_tok}')
                except (TypeError, ValueError):
                    pass

            ok = redis_cmd('hdel', 'newsletter:subscribers', email)
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            audit(sess['email'], 'subscriber_delete', email)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _messages_get(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        qs = parse_qs(urlparse(self.path).query)
        msg_id = (qs.get('id') or [''])[0].strip()
        status_filter = (qs.get('status') or ['all'])[0]
        try:
            page = max(0, int((qs.get('page') or ['0'])[0]))
        except (TypeError, ValueError):
            page = 0
        try:
            per_page = min(100, max(1, int((qs.get('per_page') or ['25'])[0])))
        except (TypeError, ValueError):
            per_page = 25

        messages = _load_messages()

        if msg_id:
            if msg_id not in messages:
                return json_response(self, 404, {'success': False, 'error': 'not found'})
            return json_response(self, 200, {'success': True, 'data': messages[msg_id]})

        ordered_ids = redis_cmd('lrange', 'contact:order', '0', '-1') or []
        ordered = []
        seen = set()
        for mid in ordered_ids:
            if mid in messages and mid not in seen:
                ordered.append(messages[mid])
                seen.add(mid)
        for mid, data in messages.items():
            if mid not in seen:
                ordered.append(data)

        if status_filter and status_filter != 'all':
            ordered = [m for m in ordered if m.get('status') == status_filter]

        total = len(ordered)
        start = page * per_page
        paginated = ordered[start:start + per_page]

        return json_response(self, 200, {
            'success': True,
            'data': paginated,
            'total': total,
            'page': page,
            'per_page': per_page,
        })

    def _messages_post(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            body = self._body()
            msg_id = (body.get('id') or '').strip()
            reply_text = (body.get('reply') or '').strip()

            if not msg_id or not reply_text or len(reply_text) > 5000:
                return json_response(self, 400, {'success': False, 'error': 'invalid reply'})

            raw = redis_cmd('hget', 'contact:messages', msg_id)
            if not raw:
                return json_response(self, 404, {'success': False, 'error': 'not found'})

            try:
                data = json.loads(raw)
            except (TypeError, ValueError):
                return json_response(self, 500, {'success': False, 'error': 'corrupt data'})

            to_email = data.get('email', '')
            name = data.get('name', 'there')
            if not to_email:
                return json_response(self, 400, {'success': False, 'error': 'no email on message'})

            try:
                _reply_email(to_email, name, reply_text, sess['email'])
            except Exception:
                return json_response(self, 500, {'success': False, 'error': 'failed to send reply'})

            data['reply'] = reply_text
            data['replied_at'] = int(time.time())
            data['status'] = 'replied'
            redis_cmd('hset', 'contact:messages', msg_id, json.dumps(data))
            redis_cmd('srem', 'contact:unread', msg_id)

            audit(sess['email'], 'message_reply', msg_id)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _messages_patch(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            body = self._body()
            msg_id = (body.get('id') or '').strip()
            status = (body.get('status') or '').strip()

            if not msg_id or status not in ('unread', 'read', 'replied', 'archived', 'spam'):
                return json_response(self, 400, {'success': False, 'error': 'invalid request'})

            raw = redis_cmd('hget', 'contact:messages', msg_id)
            if not raw:
                return json_response(self, 404, {'success': False, 'error': 'not found'})

            try:
                data = json.loads(raw)
            except (TypeError, ValueError):
                return json_response(self, 500, {'success': False, 'error': 'corrupt data'})

            data['status'] = status
            ok = redis_cmd('hset', 'contact:messages', msg_id, json.dumps(data))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            if status == 'unread':
                redis_cmd('sadd', 'contact:unread', msg_id)
            else:
                redis_cmd('srem', 'contact:unread', msg_id)

            audit(sess['email'], f'message_{status}', msg_id)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _messages_delete(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            qs = parse_qs(urlparse(self.path).query)
            msg_id = (qs.get('id') or [''])[0].strip()
            if not msg_id:
                return json_response(self, 400, {'success': False, 'error': 'id required'})

            redis_cmd('hdel', 'contact:messages', msg_id)
            redis_cmd('lrem', 'contact:order', '0', msg_id)
            redis_cmd('srem', 'contact:unread', msg_id)

            audit(sess['email'], 'message_delete', msg_id)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _projects_get(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        projects = _parse_projects(redis_cmd('hgetall', 'projects:list') or [])
        projects.sort(key=lambda p: int(p.get('order') or 0))
        return json_response(self, 200, {'success': True, 'data': projects})

    def _projects_post(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            body = self._body()

            clean, err = _validate_project(body)
            if err:
                return json_response(self, 400, {'success': False, 'error': err})

            existing = _parse_projects(redis_cmd('hgetall', 'projects:list') or [])
            max_order = max([int(p.get('order') or 0) for p in existing] + [-1])

            project_id = secrets.token_urlsafe(12)
            now = int(time.time())
            project = dict(clean)
            project.update({
                'id': project_id,
                'order': max_order + 1,
                'metrics': {},
                'created_at': now,
                'updated_at': now,
            })

            ok = redis_cmd('hset', 'projects:list', project_id, json.dumps(project))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            redis_cmd('del', 'projects:cache')
            audit(sess['email'], 'project_create', project['title'])
            return json_response(self, 200, {'success': True, 'data': project})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _projects_patch(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            body = self._body()

            if 'reorder' in body:
                order_list = body.get('reorder') or []
                if not isinstance(order_list, list):
                    return json_response(self, 400, {'success': False, 'error': 'reorder must be list'})
                for idx, pid in enumerate(order_list):
                    raw = redis_cmd('hget', 'projects:list', str(pid))
                    if not raw:
                        continue
                    try:
                        p = json.loads(raw)
                        p['order'] = idx
                        p['updated_at'] = int(time.time())
                        redis_cmd('hset', 'projects:list', str(pid), json.dumps(p))
                    except (TypeError, ValueError):
                        continue
                redis_cmd('del', 'projects:cache')
                audit(sess['email'], 'project_reorder', '', {'count': len(order_list)})
                return json_response(self, 200, {'success': True})

            project_id = (body.get('id') or '').strip()
            if not project_id:
                return json_response(self, 400, {'success': False, 'error': 'id required'})

            raw = redis_cmd('hget', 'projects:list', project_id)
            if not raw:
                return json_response(self, 404, {'success': False, 'error': 'not found'})

            try:
                existing = json.loads(raw)
            except (TypeError, ValueError):
                return json_response(self, 500, {'success': False, 'error': 'corrupt data'})

            merged = dict(existing)
            merged.update(body)
            clean, err = _validate_project(merged)
            if err:
                return json_response(self, 400, {'success': False, 'error': err})

            existing.update(clean)
            existing['updated_at'] = int(time.time())

            ok = redis_cmd('hset', 'projects:list', project_id, json.dumps(existing))
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            redis_cmd('del', 'projects:cache')
            audit(sess['email'], 'project_update', existing.get('title', ''))
            return json_response(self, 200, {'success': True, 'data': existing})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _projects_delete(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            qs = parse_qs(urlparse(self.path).query)
            project_id = (qs.get('id') or [''])[0].strip()
            if not project_id:
                return json_response(self, 400, {'success': False, 'error': 'id required'})

            raw = redis_cmd('hget', 'projects:list', project_id)
            title = ''
            if raw:
                try:
                    title = json.loads(raw).get('title', '')
                except (TypeError, ValueError):
                    pass

            ok = redis_cmd('hdel', 'projects:list', project_id)
            if ok is None:
                return json_response(self, 500, {'success': False, 'error': 'storage error'})

            redis_cmd('del', 'projects:cache')
            audit(sess['email'], 'project_delete', title)
            return json_response(self, 200, {'success': True})
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})

    def _projects_sync(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            github_token = (os.environ.get('GITHUB_TOKEN') or '').strip()

            projects = _parse_projects(redis_cmd('hgetall', 'projects:list') or [])
            headers = {'Accept': 'application/vnd.github+json'}
            if github_token:
                headers['Authorization'] = f'Bearer {github_token}'

            synced = 0
            failed = 0
            errors = []

            for p in projects:
                pid = p.get('id')
                url = p.get('github_url', '')
                owner, repo = _extract_owner_repo(url)
                if not owner or not repo:
                    continue
                try:
                    r = requests.get(
                        f'https://api.github.com/repos/{owner}/{repo}',
                        headers=headers,
                        timeout=8,
                    )
                    if r.status_code != 200:
                        failed += 1
                        errors.append(f'{owner}/{repo}: HTTP {r.status_code}')
                        continue
                    data = r.json()
                    p['metrics'] = {
                        'stars': data.get('stargazers_count', 0),
                        'forks': data.get('forks_count', 0),
                        'updated_at': data.get('pushed_at', ''),
                        'synced_at': int(time.time()),
                    }
                    p['updated_at'] = int(time.time())
                    redis_cmd('hset', 'projects:list', pid, json.dumps(p))
                    synced += 1
                except Exception as e:
                    failed += 1
                    errors.append(f'{owner}/{repo}: {str(e)[:80]}')

            redis_cmd('del', 'projects:cache')
            audit(sess['email'], 'projects_github_sync', '', {'synced': synced, 'failed': failed})
            return json_response(self, 200, {
                'success': True,
                'synced': synced,
                'failed': failed,
                'errors': errors[:10],
            })
        except Exception:
            return json_response(self, 500, {'success': False, 'error': 'server error'})