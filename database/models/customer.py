from database.db import db
from datetime import datetime

class Customer(db.Model):
    __tablename__ = 'customers'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    customer_code = db.Column(db.String(50))
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    company_name = db.Column(db.String(200))
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    country = db.Column(db.String(100))
    segment = db.Column(db.String(50))
    lifetime_value = db.Column(db.Float, default=0.0)
    acquisition_cost = db.Column(db.Float, default=0.0)
    acquisition_date = db.Column(db.Date)
    last_purchase_date = db.Column(db.Date)
    total_orders = db.Column(db.Integer, default=0)
    total_spent = db.Column(db.Float, default=0.0)
    satisfaction_score = db.Column(db.Float)
    nps_score = db.Column(db.Float)
    status = db.Column(db.String(20), default='active')
    is_churned = db.Column(db.Boolean, default=False)
    churn_date = db.Column(db.Date)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def full_name(self):
        if self.company_name:
            return self.company_name
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
    
    def to_dict(self):
        return {
            'id': self.id,
            'customer_code': self.customer_code,
            'name': self.full_name(),
            'email': self.email,
            'segment': self.segment,
            'lifetime_value': self.lifetime_value,
            'total_spent': self.total_spent,
            'total_orders': self.total_orders,
            'satisfaction_score': self.satisfaction_score,
            'status': self.status,
            'is_churned': self.is_churned,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }