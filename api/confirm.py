import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
SITE_URL = os.environ.get("SITE_URL", "https://kaifansari.me")


def redis_cmd(*args):
    url = UPSTASH_URL.rstrip("/") + "/" + "/".join(str(a) for a in args)
    res = requests.get(url, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, timeout=5)
    return res.json().get("result") if res.status_code == 200 else None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        qs = parse_qs(urlparse(self.path).query)
        token = (qs.get("token") or [""])[0]

        if not token:
            return self.redirect(f"{SITE_URL}/?subscribed=0")

        email = redis_cmd("get", f"pending:{token}")
        if not email:
            return self.redirect(f"{SITE_URL}/?subscribed=0")

        redis_cmd("set", f"confirmed:{email}", "1")
        redis_cmd("delete", f"pending:{token}")

        return self.redirect(f"{SITE_URL}/?subscribed=1")

    def redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.end_headers()