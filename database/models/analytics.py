from database.db import db
from datetime import datetime
import json

class Analytics(db.Model):
    __tablename__ = 'analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    metric_name = db.Column(db.String(100), nullable=False)
    metric_category = db.Column(db.String(50))
    metric_value = db.Column(db.Float)
    metric_data = db.Column(db.Text)
    period_start = db.Column(db.Date)
    period_end = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_metric_data(self):
        return json.loads(self.metric_data) if self.metric_data else {}
    
    def set_metric_data(self, data):
        self.metric_data = json.dumps(data)
    
    def to_dict(self):
        return {
            'id': self.id,
            'metric_name': self.metric_name,
            'metric_category': self.metric_category,
            'metric_value': self.metric_value,
            'period_start': self.period_start.isoformat() if self.period_start else None,
            'period_end': self.period_end.isoformat() if self.period_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }