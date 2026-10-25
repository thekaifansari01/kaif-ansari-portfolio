import json
import os
import secrets
import smtplib
import time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler

import requests

SECRET_KEY = os.environ.get("TURNSTILE_SECRET_KEY")
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("SMTP_USER")
SMTP_PASS = os.environ.get("SMTP_PASS")
FROM_EMAIL = os.environ.get("NEWSLETTER_FROM", SMTP_USER)
SITE_URL = os.environ.get("SITE_URL", "https://kaifansari.me")

UPSTASH_URL = os.environ.get("UPSTASH_REDIS_REST_URL")
UPSTASH_TOKEN = os.environ.get("UPSTASH_REDIS_REST_TOKEN")


def redis_cmd(*args):
    if not UPSTASH_URL or not UPSTASH_TOKEN:
        return None
    url = UPSTASH_URL.rstrip("/") + "/" + "/".join(str(a) for a in args)
    res = requests.get(url, headers={"Authorization": f"Bearer {UPSTASH_TOKEN}"}, timeout=5)
    if res.status_code != 200:
        return None
    return res.json().get("result")


def verify_turnstile(token, ip):
    if not token:
        return False
    try:
        r = requests.post(
            "https://challenges.cloudflare.com/turnstile/v0/siteverify",
            data={"secret": SECRET_KEY, "response": token, "remoteip": ip},
            timeout=5,
        )
        return r.json().get("success", False)
    except Exception:
        return False


def rate_limit(ip):
    key = f"rl:nl:{ip}"
    count = redis_cmd("incr", key)
    if count == 1:
        redis_cmd("expire", key, 3600)
    return int(count or 0) <= 5


def send_confirmation(email, token):
    link = f"{SITE_URL}/api/confirm?token={token}"
    msg = EmailMessage()
    msg["Subject"] = "Confirm your subscription — kaif ansari"
    msg["From"] = FROM_EMAIL
    msg["To"] = email
    msg.set_content(
        f"Confirm your subscription:\n\n{link}\n\n"
        "If you didn't request this, ignore this email.\n"
    )
    msg.add_alternative(
        f"""
        <div style="font-family:Arial,sans-serif;max-width:520px;margin:0 auto;padding:24px;">
          <h2 style="margin:0 0 12px;">confirm your subscription</h2>
          <p style="color:#444;line-height:1.6;">
            Click the button below to confirm you want build logs, new agents,
            and experiments from kaif.
          </p>
          <p style="margin:24px 0;">
            <a href="{link}" style="display:inline-block;padding:12px 20px;background:#c8ff00;color:#0a0a0a;text-decoration:none;border-radius:4px;font-weight:700;">
              confirm subscription
            </a>
          </p>
          <p style="font-size:12px;color:#888;">
            If you didn't request this, ignore this email.
          </p>
        </div>
        """,
        subtype="html",
    )

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)
        server.send_message(msg)


class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            data = json.loads(self.rfile.read(length))
            email = (data.get("email") or "").strip().lower()
            token = data.get("token") or ""
            ip = self.headers.get("x-forwarded-for", "").split(",")[0].strip()

            if "@" not in email:
                return self.json(400, {"success": False, "error": "invalid email"})

            if not verify_turnstile(token, ip):
                return self.json(400, {"success": False, "error": "captcha failed"})

            if not rate_limit(ip or "unknown"):
                return self.json(429, {"success": False, "error": "too many attempts"})

            if redis_cmd("get", f"confirmed:{email}"):
                return self.json(200, {"success": True, "message": "already subscribed"})

            confirm_token = secrets.token_urlsafe(32)
            redis_cmd("set", f"pending:{confirm_token}", email)
            redis_cmd("expire", f"pending:{confirm_token}", 86400)

            send_confirmation(email, confirm_token)

            return self.json(200, {"success": True, "message": "confirmation sent"})
        except Exception as e:
            return self.json(500, {"success": False, "error": str(e)})

    def json(self, status, payload):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())