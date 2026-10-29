from http.server import BaseHTTPRequestHandler

from session_lib import (
    clear_cookie, get_session, redis_cmd, audit, cors_origin, handle_options,
)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        handle_options(self)

    def do_POST(self):
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