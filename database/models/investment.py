from database.db import db
from datetime import datetime

class Investment(db.Model):
    __tablename__ = 'investments'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    investment_type = db.Column(db.String(50))
    category = db.Column(db.String(100))
    amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    expected_return_rate = db.Column(db.Float, default=0.0)
    actual_return_rate = db.Column(db.Float)
    risk_level = db.Column(db.String(20), default='medium')
    start_date = db.Column(db.Date)
    maturity_date = db.Column(db.Date)
    current_value = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    institution = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'investment_type': self.investment_type,
            'amount': self.amount,
            'expected_return_rate': self.expected_return_rate,
            'actual_return_rate': self.actual_return_rate,
            'risk_level': self.risk_level,
            'current_value': self.current_value,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }