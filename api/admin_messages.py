import json
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from session_lib import (
    get_session, json_response, handle_options, redis_cmd, audit, SITE_URL,
)
from mailer_lib import smtp_send


def load_messages():
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
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
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

        messages = load_messages()

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

    def do_PATCH(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
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

    def do_DELETE(self):
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

    def do_POST(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')
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

            try:
                smtp_send(to_email, subject, plain, html, reply_to=sess['email'])
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