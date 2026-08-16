from database.db import db
from datetime import datetime

class ExportHistory(db.Model):
    __tablename__ = 'export_history'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    export_type = db.Column(db.String(50), nullable=False)
    export_format = db.Column(db.String(20), nullable=False)
    file_path = db.Column(db.String(255))
    file_size = db.Column(db.Integer)
    record_count = db.Column(db.Integer)
    filters_used = db.Column(db.Text)
    status = db.Column(db.String(20), default='success')
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'export_type': self.export_type,
            'export_format': self.export_format,
            'file_path': self.file_path,
            'file_size': self.file_size,
            'record_count': self.record_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }