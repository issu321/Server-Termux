from database.db import db
from datetime import datetime

class Employee(db.Model):
    __tablename__ = 'employees'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    employee_id = db.Column(db.String(50))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120))
    phone = db.Column(db.String(50))
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'))
    job_title = db.Column(db.String(200))
    employment_type = db.Column(db.String(50), default='full_time')
    salary = db.Column(db.Float, default=0.0)
    benefits_cost = db.Column(db.Float, default=0.0)
    hire_date = db.Column(db.Date)
    termination_date = db.Column(db.Date)
    status = db.Column(db.String(20), default='active')
    performance_rating = db.Column(db.Float)
    skills = db.Column(db.Text)
    manager_id = db.Column(db.Integer, db.ForeignKey('employees.id'))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    subordinates = db.relationship('Employee', remote_side=[id], backref='manager')
    
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def total_cost(self):
        return self.salary + self.benefits_cost
    
    def to_dict(self):
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'email': self.email,
            'job_title': self.job_title,
            'department_id': self.department_id,
            'salary': self.salary,
            'benefits_cost': self.benefits_cost,
            'status': self.status,
            'performance_rating': self.performance_rating,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }