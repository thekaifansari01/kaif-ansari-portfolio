import html as html_lib
import json
import os
import re

from session_lib import SITE_URL, redis_cmd
from mailer_lib import smtp_send

NEWSLETTER_FROM = os.environ.get(
    'NEWSLETTER_FROM',
    'Kaif Ansari <newsletter@kaifansari.me>'
)


def _strip_html(text):
    text = re.sub(r'<script\b[^<]*(?:(?!</script>)<[^<]*)*</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style\b[^<]*(?:(?!</style>)<[^<]*)*</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<[^>]+>', '', text)
    text = html_lib.unescape(text)
    return text.strip()


def _wrap_plain(content, subject, unsub_url):
    safe_subject = html_lib.escape(subject)
    safe_content = html_lib.escape(content).replace('\n', '<br>')
    unsub_html = ''
    if unsub_url:
        unsub_html = (
            '<p style="margin:0;font-family:\'Courier New\',Consolas,monospace;'
            'font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">'
            '<a href="' + html_lib.escape(unsub_url) + '" '
            'style="color:#6a6a6a;text-decoration:underline;">UNSUBSCRIBE</a></p>'
        )
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<title>' + safe_subject + '</title></head>'
        '<body style="margin:0;padding:0;background:#0a0a0a;font-family:Arial,sans-serif;">'
        '<table cellpadding="0" cellspacing="0" border="0" width="100%" '
        'style="background:#0a0a0a;padding:40px 20px;"><tr><td align="center">'
        '<table cellpadding="0" cellspacing="0" border="0" width="100%" '
        'style="max-width:540px;">'
        '<tr><td style="padding-bottom:20px;">'
        '<span style="display:inline-block;padding:8px 14px;background:#c8ff00;'
        'color:#0a0a0a;border:2px solid #f5efe3;font-family:\'Courier New\',monospace;'
        'font-size:14px;font-weight:700;letter-spacing:0.5px;border-radius:3px;">~/kaif</span>'
        '</td></tr>'
        '<tr><td style="background:#121212;border:3px solid #f5efe3;border-radius:4px;'
        'box-shadow:8px 8px 0 #c8ff00;padding:36px 28px;">'
        '<span style="display:inline-block;padding:5px 12px;background:#c8ff00;'
        'color:#0a0a0a;border:2px solid #0a0a0a;font-family:\'Courier New\',monospace;'
        'font-size:11px;font-weight:700;letter-spacing:1px;text-transform:lowercase;'
        'border-radius:2px;">[ newsletter ]</span>'
        '<h1 style="margin:20px 0 20px;font-family:Impact,\'Arial Black\',sans-serif;'
        'font-size:34px;line-height:0.95;color:#f5efe3;text-transform:uppercase;'
        'font-weight:400;">' + safe_subject + '</h1>'
        '<div style="font-family:\'Courier New\',Consolas,monospace;font-size:14px;'
        'line-height:1.75;color:#e0e0e0;">' + safe_content + '</div>'
        '<div style="margin-top:36px;padding-top:22px;border-top:2px solid #333;">'
        '<p style="margin:0 0 10px;font-family:\'Courier New\',Consolas,monospace;'
        'font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">SENT BY KAIF ANSARI &middot; '
        '<a href="' + SITE_URL + '" style="color:#c8ff00;text-decoration:none;">kaifansari.me</a>'
        '</p>' + unsub_html + '</div>'
        '</td></tr></table></td></tr></table></body></html>'
    )


def _wrap_html(content, subject, unsub_url):
    safe_subject = html_lib.escape(subject)
    unsub_html = ''
    if unsub_url:
        unsub_html = (
            '<p style="margin:0;font-family:\'Courier New\',Consolas,monospace;'
            'font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">'
            '<a href="' + html_lib.escape(unsub_url) + '" '
            'style="color:#6a6a6a;text-decoration:underline;">UNSUBSCRIBE</a></p>'
        )
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<title>' + safe_subject + '</title>'
        '<style>body{margin:0;padding:0;background:#0a0a0a;font-family:Arial,sans-serif;}</style>'
        '</head><body style="margin:0;padding:0;background:#0a0a0a;">'
        '<table cellpadding="0" cellspacing="0" border="0" width="100%" '
        'style="background:#0a0a0a;padding:40px 20px;"><tr><td align="center">'
        '<table cellpadding="0" cellspacing="0" border="0" width="100%" '
        'style="max-width:540px;">'
        '<tr><td style="padding-bottom:20px;">'
        '<span style="display:inline-block;padding:8px 14px;background:#c8ff00;'
        'color:#0a0a0a;border:2px solid #f5efe3;font-family:\'Courier New\',monospace;'
        'font-size:14px;font-weight:700;letter-spacing:0.5px;border-radius:3px;">~/kaif</span>'
        '</td></tr>'
        '<tr><td style="background:#121212;border:3px solid #f5efe3;border-radius:4px;'
        'box-shadow:8px 8px 0 #c8ff00;padding:36px 28px;">'
        '<span style="display:inline-block;padding:5px 12px;background:#c8ff00;'
        'color:#0a0a0a;border:2px solid #0a0a0a;font-family:\'Courier New\',monospace;'
        'font-size:11px;font-weight:700;letter-spacing:1px;text-transform:lowercase;'
        'border-radius:2px;">[ newsletter ]</span>'
        '<div style="margin-top:20px;color:#e0e0e0;">' + content + '</div>'
        '<div style="margin-top:36px;padding-top:22px;border-top:2px solid #333;">'
        '<p style="margin:0 0 10px;font-family:\'Courier New\',Consolas,monospace;'
        'font-size:11px;color:#6a6a6a;letter-spacing:1.5px;">SENT BY KAIF ANSARI &middot; '
        '<a href="' + SITE_URL + '" style="color:#c8ff00;text-decoration:none;">kaifansari.me</a>'
        '</p>' + unsub_html + '</div>'
        '</td></tr></table></td></tr></table></body></html>'
    )


def send_news_email(to_email, subject, content, is_html=False, unsub_token=None):
    unsub_url = ''
    if unsub_token:
        unsub_url = SITE_URL + '/api/unsubscribe?token=' + unsub_token

    if is_html:
        html_body = _wrap_html(content, subject, unsub_url)
        text_body = _strip_html(content)
        if unsub_url:
            text_body = text_body + '\n\n---\nunsubscribe: ' + unsub_url
    else:
        html_body = _wrap_plain(content, subject, unsub_url)
        text_body = content
        if unsub_url:
            text_body = text_body + '\n\n---\nunsubscribe: ' + unsub_url

    smtp_send(to_email, subject, text_body, html_body, from_email=NEWSLETTER_FROM)


def get_audience(audience):
    raw = redis_cmd('hgetall', 'newsletter:subscribers') or []
    result = []
    if not isinstance(raw, list):
        return result

    for i in range(0, len(raw), 2):
        try:
            email = raw[i]
            data = json.loads(raw[i + 1])
            status = data.get('status', '')
            if audience == 'confirmed' and status != 'confirmed':
                continue
            if audience == 'all' and status not in ('confirmed', 'pending'):
                continue
            unsub = data.get('unsub_token') or ''
            result.append({'email': email, 'unsub': unsub})
        except (IndexError, TypeError, ValueError):
            continue

    return result