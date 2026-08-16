from database.db import db
from datetime import datetime

class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)
    format = db.Column(db.String(20), default='pdf')
    file_path = db.Column(db.String(255))
    parameters = db.Column(db.Text)
    summary = db.Column(db.Text)
    page_count = db.Column(db.Integer)
    file_size = db.Column(db.Integer)
    is_scheduled = db.Column(db.Boolean, default=False)
    schedule_frequency = db.Column(db.String(20))
    last_generated = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='reports')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'report_type': self.report_type,
            'format': self.format,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'page_count': self.page_count,
            'is_scheduled': self.is_scheduled,
            'last_generated': self.last_generated.isoformat() if self.last_generated else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }