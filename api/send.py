import json
import os
import requests
import smtplib
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler

# Environment variables
SECRET_KEY = os.environ.get('TURNSTILE_SECRET_KEY')
SMTP_HOST = os.environ.get('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.environ.get('SMTP_PORT', 587))
SMTP_USER = os.environ.get('SMTP_USER')
SMTP_PASS = os.environ.get('SMTP_PASS')
TO_EMAIL = os.environ.get('TO_EMAIL', 'kaif.ansari.global@gmail.com')

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_POST(self):
        try:
            # Read request
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length)
            data = json.loads(body)
            
            name = data.get('name', '')
            email = data.get('email', '')
            message = data.get('message', '')
            token = data.get('token', '')
            
            # Log
            print(f"📝 New submission from {name} ({email})")
            
            # Verify Turnstile
            if not token:
                self.send_json_response(400, {'success': False, 'error': 'Missing CAPTCHA token'})
                return
            
            verify_url = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'
            resp = requests.post(verify_url, data={'secret': SECRET_KEY, 'response': token}, timeout=5)
            result = resp.json()
            
            if not result.get('success'):
                self.send_json_response(400, {'success': False, 'error': 'CAPTCHA verification failed'})
                return
            
            # ✅ Send Email
            email_sent = self.send_email(name, email, message)
            
            if email_sent:
                self.send_json_response(200, {'success': True, 'message': 'Email sent successfully!'})
            else:
                self.send_json_response(500, {'success': False, 'error': 'Failed to send email'})
                
        except Exception as e:
            print(f"❌ Error: {e}")
            self.send_json_response(500, {'success': False, 'error': str(e)})
    
    def send_email(self, name, email, message):
        """Send email via SMTP"""
        if not SMTP_USER or not SMTP_PASS:
            print("⚠️ SMTP credentials not configured")
            return False
        
        try:
            msg = EmailMessage()
            msg.set_content(f"""
Name: {name}
Email: {email}
Message:
{message}
""")
            msg['Subject'] = f'📬 New Contact Form from {name}'
            msg['From'] = SMTP_USER
            msg['To'] = TO_EMAIL
            msg['Reply-To'] = email
            
            with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
                server.starttls()
                server.login(SMTP_USER, SMTP_PASS)
                server.send_message(msg)
            
            print(f"✅ Email sent to {TO_EMAIL}")
            return True
        except Exception as e:
            print(f"❌ SMTP Error: {e}")
            return False
    
    def send_json_response(self, status_code, data):
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())