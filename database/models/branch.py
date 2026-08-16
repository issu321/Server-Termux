from database.db import db
from datetime import datetime

class Branch(db.Model):
    __tablename__ = 'branches'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    country = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    phone = db.Column(db.String(50))
    email = db.Column(db.String(120))
    branch_type = db.Column(db.String(50), default='office')
    is_main = db.Column(db.Boolean, default=False)
    square_footage = db.Column(db.Float)
    monthly_rent = db.Column(db.Float, default=0.0)
    employee_count = db.Column(db.Integer, default=0)
    manager_name = db.Column(db.String(200))
    status = db.Column(db.String(20), default='active')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'city': self.city,
            'country': self.country,
            'branch_type': self.branch_type,
            'is_main': self.is_main,
            'employee_count': self.employee_count,
            'monthly_rent': self.monthly_rent,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }