from database.db import db
from datetime import datetime

class Department(db.Model):
    __tablename__ = 'departments'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    code = db.Column(db.String(50))
    description = db.Column(db.Text)
    head_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    head_name = db.Column(db.String(200))
    budget = db.Column(db.Float, default=0.0)
    spent = db.Column(db.Float, default=0.0)
    employee_count = db.Column(db.Integer, default=0)
    color = db.Column(db.String(20), default='#00D4FF')
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship to employees — enables dept.employees query
    employees = db.relationship('Employee', backref='department', lazy='dynamic')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'head_name': self.head_name,
            'budget': self.budget,
            'spent': self.spent,
            'employee_count': self.employee_count,
            'color': self.color,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }