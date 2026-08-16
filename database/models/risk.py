from database.db import db
from datetime import datetime
import json

class Risk(db.Model):
    __tablename__ = 'risks'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    probability = db.Column(db.Float, default=0.5)
    impact = db.Column(db.Float, default=0.5)
    risk_score = db.Column(db.Float, default=0.0)
    risk_level = db.Column(db.String(20), default='medium')
    status = db.Column(db.String(20), default='active')
    mitigation_plan = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    review_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    factors = db.relationship('RiskFactor', backref='risk', lazy='dynamic', cascade='all, delete-orphan')
    
    def calculate_score(self):
        self.risk_score = (self.probability * self.impact) * 100
        if self.risk_score >= 70:
            self.risk_level = 'critical'
        elif self.risk_score >= 40:
            self.risk_level = 'high'
        elif self.risk_score >= 20:
            self.risk_level = 'medium'
        else:
            self.risk_level = 'low'
        return self.risk_score
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'probability': self.probability,
            'impact': self.impact,
            'risk_score': self.risk_score,
            'risk_level': self.risk_level,
            'status': self.status,
            'review_date': self.review_date.isoformat() if self.review_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class RiskFactor(db.Model):
    __tablename__ = 'risk_factors'
    
    id = db.Column(db.Integer, primary_key=True)
    risk_id = db.Column(db.Integer, db.ForeignKey('risks.id'), nullable=False)
    factor_name = db.Column(db.String(200), nullable=False)
    weight = db.Column(db.Float, default=1.0)
    score = db.Column(db.Float, default=0.0)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)