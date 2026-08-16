from database.db import db
from datetime import datetime

class MarketData(db.Model):
    __tablename__ = 'market_data'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    market_name = db.Column(db.String(200))
    industry = db.Column(db.String(100))
    region = db.Column(db.String(100))
    metric_name = db.Column(db.String(100), nullable=False)
    metric_value = db.Column(db.Float)
    currency = db.Column(db.String(10), default='USD')
    period = db.Column(db.String(20))
    year = db.Column(db.Integer)
    quarter = db.Column(db.Integer)
    source = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'market_name': self.market_name,
            'industry': self.industry,
            'region': self.region,
            'metric_name': self.metric_name,
            'metric_value': self.metric_value,
            'period': self.period,
            'year': self.year,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }