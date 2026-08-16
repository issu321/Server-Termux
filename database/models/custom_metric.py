from database.db import db
from datetime import datetime
import json

class CustomMetric(db.Model):
    __tablename__ = 'custom_metrics'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    formula = db.Column(db.Text)
    data_source = db.Column(db.String(100))
    config = db.Column(db.Text)
    last_value = db.Column(db.Float)
    last_calculated = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def get_config(self):
        return json.loads(self.config) if self.config else {}
    
    def set_config(self, conf):
        self.config = json.dumps(conf)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'formula': self.formula,
            'data_source': self.data_source,
            'last_value': self.last_value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }