from database.db import db
from datetime import datetime

class Supplier(db.Model):
    __tablename__ = 'suppliers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    category = db.Column(db.String(100))
    payment_terms = db.Column(db.String(100))
    lead_time_days = db.Column(db.Integer, default=0)
    rating = db.Column(db.Float, default=3.0)
    quality_score = db.Column(db.Float)
    reliability_score = db.Column(db.Float)
    cost_rating = db.Column(db.Float)
    total_spend = db.Column(db.Float, default=0.0)
    total_orders = db.Column(db.Integer, default=0)
    is_primary = db.Column(db.Boolean, default=False)
    status = db.Column(db.String(20), default='active')
    contract_start = db.Column(db.Date)
    contract_end = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'city': self.city,
            'country': self.country,
            'category': self.category,
            'payment_terms': self.payment_terms,
            'lead_time_days': self.lead_time_days,
            'rating': self.rating,
            'quality_score': self.quality_score,
            'reliability_score': self.reliability_score,
            'cost_rating': self.cost_rating,
            'total_spend': self.total_spend,
            'total_orders': self.total_orders,
            'is_primary': self.is_primary,
            'status': self.status,
            'contract_start': self.contract_start.isoformat() if self.contract_start else None,
            'contract_end': self.contract_end.isoformat() if self.contract_end else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }