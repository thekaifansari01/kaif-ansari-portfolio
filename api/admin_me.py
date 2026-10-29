from http.server import BaseHTTPRequestHandler

from _session import get_session, json_response, handle_options


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_GET(self):
        sess = get_session(self)
        if not sess:
            return json_response(self, 401, {'success': False, 'error': 'unauthorized'})
        return json_response(self, 200, {'success': True, 'email': sess['email']})