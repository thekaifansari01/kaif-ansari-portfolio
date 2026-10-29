import json
import secrets
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

from session_lib import get_session, json_response, handle_options, redis_cmd, audit


VALID_STATUS = ('live', 'shipped', 'wip')


def parse_projects(raw):
    projects = []
    if not isinstance(raw, list):
        return projects
    for i in range(0, len(raw), 2):
        try:
            projects.append(json.loads(raw[i + 1]))
        except (IndexError, TypeError, ValueError):
            pass
    return projects


def validate(body):
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
    if status not in VALID_STATUS:
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


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        projects = parse_projects(redis_cmd('hgetall', 'projects:list') or [])
        projects.sort(key=lambda p: int(p.get('order') or 0))
        return json_response(self, 200, {'success': True, 'data': projects})

    def do_POST(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')

            clean, err = validate(body)
            if err:
                return json_response(self, 400, {'success': False, 'error': err})

            existing = parse_projects(redis_cmd('hgetall', 'projects:list') or [])
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

    def do_PATCH(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            length = int(self.headers.get('Content-Length', 0))
            body = json.loads(self.rfile.read(length) or b'{}')

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
            clean, err = validate(merged)
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

    def do_DELETE(self):
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