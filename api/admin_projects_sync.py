import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler

import requests

from session_lib import get_session, json_response, handle_options, redis_cmd, audit


GITHUB_TOKEN = (os.environ.get('GITHUB_TOKEN') or '').strip()


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


def extract_owner_repo(url):
    if not url:
        return None, None
    m = re.match(r'https?://github\.com/([^/]+)/([^/?#]+)', url)
    if not m:
        return None, None
    return m.group(1), m.group(2).rstrip('/').replace('.git', '')


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})

        try:
            projects = parse_projects(redis_cmd('hgetall', 'projects:list') or [])
            headers = {'Accept': 'application/vnd.github+json'}
            if GITHUB_TOKEN:
                headers['Authorization'] = f'Bearer {GITHUB_TOKEN}'

            synced = 0
            failed = 0
            errors = []

            for p in projects:
                pid = p.get('id')
                url = p.get('github_url', '')
                owner, repo = extract_owner_repo(url)
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