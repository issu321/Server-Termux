from database.db import db
from datetime import datetime

class Competitor(db.Model):
    __tablename__ = 'competitors'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    website = db.Column(db.String(255))
    industry = db.Column(db.String(100))
    market_share = db.Column(db.Float, default=0.0)
    revenue_estimate = db.Column(db.Float)
    employee_count = db.Column(db.Integer)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    pricing_strategy = db.Column(db.Text)
    market_position = db.Column(db.String(50))
    threat_level = db.Column(db.String(20), default='medium')
    last_updated = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'website': self.website,
            'market_share': self.market_share,
            'revenue_estimate': self.revenue_estimate,
            'employee_count': self.employee_count,
            'threat_level': self.threat_level,
            'market_position': self.market_position,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }