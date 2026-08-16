from database.db import db
from datetime import datetime

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    loan_name = db.Column(db.String(200), nullable=False)
    lender_name = db.Column(db.String(200))
    loan_type = db.Column(db.String(50))
    principal_amount = db.Column(db.Float, default=0.0)
    interest_rate = db.Column(db.Float, default=0.0)
    tenure_months = db.Column(db.Integer, default=0)
    emi_amount = db.Column(db.Float, default=0.0)
    total_interest = db.Column(db.Float, default=0.0)
    total_amount = db.Column(db.Float, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)
    remaining_amount = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    purpose = db.Column(db.Text)
    collateral = db.Column(db.Text)
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_emi(self):
        if self.principal_amount > 0 and self.interest_rate > 0 and self.tenure_months > 0:
            r = self.interest_rate / (12 * 100)
            n = self.tenure_months
            self.emi_amount = self.principal_amount * r * (1 + r)**n / ((1 + r)**n - 1)
            self.total_amount = self.emi_amount * n
            self.total_interest = self.total_amount - self.principal_amount
            self.remaining_amount = self.total_amount - self.amount_paid
        return self.emi_amount
    
    def to_dict(self):
        return {
            'id': self.id,
            'loan_name': self.loan_name,
            'lender_name': self.lender_name,
            'principal_amount': self.principal_amount,
            'interest_rate': self.interest_rate,
            'tenure_months': self.tenure_months,
            'emi_amount': self.emi_amount,
            'total_interest': self.total_interest,
            'remaining_amount': self.remaining_amount,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }