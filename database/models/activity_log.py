from database.db import db
from datetime import datetime

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user_name = db.Column(db.String(200))
    activity_type = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    module = db.Column(db.String(50))
    icon = db.Column(db.String(50), default='activity')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_name': self.user_name,
            'activity_type': self.activity_type,
            'description': self.description,
            'module': self.module,
            'icon': self.icon,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }