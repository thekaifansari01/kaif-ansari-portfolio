import os
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

import requests

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")
SITE_URL = os.environ.get("SITE_URL", "https://kaifansari.me").rstrip("/")


def redis_cmd(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    try:
        url = UPSTASH_URL.rstrip("/") + "/" + "/".join(str(a) for a in args)
        res = requests.get(url, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, timeout=5)
        if res.status_code != 200:
            return None
        return res.json().get("result")
    except Exception:
        return None


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            qs = parse_qs(urlparse(self.path).query)
            token = (qs.get("token") or [""])[0].strip()

            if not token or len(token) < 10:
                return self.redirect(f"{SITE_URL}/?subscribed=0")

            email = redis_cmd("get", f"pending:{token}")
            if not email:
                return self.redirect(f"{SITE_URL}/?subscribed=0")

            existing = redis_cmd("get", f"confirmed:{email}")
            if existing:
                return self.redirect(f"{SITE_URL}/?subscribed=1")

            result = redis_cmd("set", f"confirmed:{email}", "1")
            if result is None:
                return self.redirect(f"{SITE_URL}/?subscribed=0")

            return self.redirect(f"{SITE_URL}/?subscribed=1")

        except Exception as e:
            print(f"❌ confirm error: {e}")
            return self.redirect(f"{SITE_URL}/?subscribed=0")

    def redirect(self, url):
        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
        self.send_header("Pragma", "no-cache")
        self.send_header("Expires", "0")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()