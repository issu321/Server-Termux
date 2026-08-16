import jwt
import secrets
from datetime import datetime, timedelta
from flask import current_app

def generate_token(data, expires_in=3600):
    payload = {
        'data': data,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow(),
        'jti': secrets.token_hex(16)
    }
    return jwt.encode(payload, current_app.config['SECRET_KEY'], algorithm='HS256')

def verify_token(token):
    try:
        payload = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
        return payload.get('data')
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None

def generate_csrf_token():
    return secrets.token_urlsafe(32)