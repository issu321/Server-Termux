from database.db import db
from database.models.user import User
from database.models.company import Company
from database.models.audit_log import AuditLog
from security.password_hash import hash_password, verify_password
from security.rate_limiter import limiter
from datetime import datetime

class AuthService:
    @staticmethod
    def authenticate(username, password, ip_address=None):
        if not limiter.is_allowed(f"login:{username}"):
            return None, "Too many login attempts. Please try again later."
        
        user = User.query.filter(
            (User.username == username) | (User.email == username)
        ).first()
        
        if not user:
            return None, "Invalid credentials"
        
        if user.is_locked():
            return None, "Account is temporarily locked"
        
        if not verify_password(password, user.password_hash):
            user.login_attempts += 1
            if user.login_attempts >= 5:
                from datetime import timedelta
                user.locked_until = datetime.utcnow() + timedelta(minutes=15)
            db.session.commit()
            return None, "Invalid credentials"
        
        user.login_attempts = 0
        user.locked_until = None
        user.last_login = datetime.utcnow()
        db.session.commit()
        
        limiter.reset(f"login:{username}")
        return user, None
    
    @staticmethod
    def register_user(username, email, password, first_name=None, last_name=None, role='Analyst'):
        if User.query.filter_by(username=username).first():
            return None, "Username already exists"
        if User.query.filter_by(email=email).first():
            return None, "Email already exists"
        
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            role=role,
            is_admin=(role == 'Admin')
        )
        user.password_hash = hash_password(password)
        db.session.add(user)
        db.session.commit()
        return user, None
    
    @staticmethod
    def log_action(user_id, username, action, resource_type=None, resource_id=None, details=None, ip_address=None, status='success'):
        log = AuditLog(
            user_id=user_id,
            username=username,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            status=status
        )
        db.session.add(log)
        db.session.commit()
        return log