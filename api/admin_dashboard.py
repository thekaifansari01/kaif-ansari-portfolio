import json
import time
from http.server import BaseHTTPRequestHandler

from _session import get_session, json_response, handle_options, redis_cmd


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
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