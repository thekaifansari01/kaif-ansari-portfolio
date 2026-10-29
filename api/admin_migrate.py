import json
import time
from http.server import BaseHTTPRequestHandler

from _session import (
    get_session, json_response, handle_options, redis_cmd, scan_all, audit,
)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
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