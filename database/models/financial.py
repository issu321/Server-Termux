from database.db import db
from datetime import datetime

class FinancialRecord(db.Model):
    __tablename__ = 'financial_records'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'))
    transaction_date = db.Column(db.Date, nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    category = db.Column(db.String(100))
    subcategory = db.Column(db.String(100))
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text)
    reference_number = db.Column(db.String(100))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'))
    is_recurring = db.Column(db.Boolean, default=False)
    recurring_frequency = db.Column(db.String(20))
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'account_id': self.account_id,
            'transaction_date': self.transaction_date.isoformat() if self.transaction_date else None,
            'transaction_type': self.transaction_type,
            'category': self.category,
            'subcategory': self.subcategory,
            'amount': self.amount,
            'description': self.description,
            'reference_number': self.reference_number,
            'department_id': self.department_id,
            'project_id': self.project_id,
            'is_recurring': self.is_recurring,
            'recurring_frequency': self.recurring_frequency,
            'created_by': self.created_by,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FinancialAccount(db.Model):
    __tablename__ = 'financial_accounts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    account_name = db.Column(db.String(200), nullable=False)
    account_type = db.Column(db.String(50), nullable=False)
    account_category = db.Column(db.String(50))
    parent_account_id = db.Column(db.Integer, db.ForeignKey('financial_accounts.id'))
    opening_balance = db.Column(db.Float, default=0.0)
    current_balance = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    is_active = db.Column(db.Boolean, default=True)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sub_accounts = db.relationship('FinancialAccount', remote_side=[id], backref='parent_account')
    
    def to_dict(self):
        return {
            'id': self.id,
            'account_name': self.account_name,
            'account_type': self.account_type,
            'current_balance': self.current_balance,
            'opening_balance': self.opening_balance,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }