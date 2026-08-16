from database.db import db
from datetime import datetime

class ImportHistory(db.Model):
    __tablename__ = 'import_history'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    import_type = db.Column(db.String(50), nullable=False)
    file_name = db.Column(db.String(255))
    file_format = db.Column(db.String(20))
    record_count = db.Column(db.Integer)
    success_count = db.Column(db.Integer, default=0)
    error_count = db.Column(db.Integer, default=0)
    error_details = db.Column(db.Text)
    status = db.Column(db.String(20), default='processing')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'import_type': self.import_type,
            'file_name': self.file_name,
            'file_format': self.file_format,
            'record_count': self.record_count,
            'success_count': self.success_count,
            'error_count': self.error_count,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }