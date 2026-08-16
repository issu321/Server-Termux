from database.db import db
from datetime import datetime

class ThemePreference(db.Model):
    __tablename__ = 'themes'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    theme_id = db.Column(db.String(50), default='aurora_enterprise')
    accent_color = db.Column(db.String(20))
    font_size = db.Column(db.String(10), default='medium')
    animation_speed = db.Column(db.String(10), default='normal')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'theme_id': self.theme_id,
            'accent_color': self.accent_color,
            'font_size': self.font_size,
            'animation_speed': self.animation_speed,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }