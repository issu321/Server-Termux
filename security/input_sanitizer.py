import bleach
import re
from html import escape

ALLOWED_TAGS = ['p', 'br', 'strong', 'em', 'u', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                'ul', 'ol', 'li', 'a', 'span', 'div']
ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title'],
    'span': ['style'],
    'div': ['class']
}

def sanitize_input(text, max_length=None):
    if not text:
        return ''
    text = escape(text)
    if max_length and len(text) > max_length:
        text = text[:max_length]
    return text.strip()

def sanitize_html(html_content):
    if not html_content:
        return ''
    return bleach.clean(html_content, tags=ALLOWED_TAGS, attributes=ALLOWED_ATTRIBUTES, strip=True)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_phone(phone):
    pattern = r'^[+]?[\d\s-]{8,20}$'
    return re.match(pattern, phone) is not None

def sanitize_filename(filename):
    return re.sub(r'[^\w\s.-]', '', filename).strip()