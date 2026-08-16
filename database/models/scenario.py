from database.db import db
from datetime import datetime
import json

class Scenario(db.Model):
    __tablename__ = 'scenarios'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    scenario_type = db.Column(db.String(50))
    is_active = db.Column(db.Boolean, default=True)
    base_parameters = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    steps = db.relationship('ScenarioStep', backref='scenario', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_parameters(self):
        return json.loads(self.base_parameters) if self.base_parameters else {}
    
    def set_parameters(self, params):
        self.base_parameters = json.dumps(params)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'scenario_type': self.scenario_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ScenarioStep(db.Model):
    __tablename__ = 'scenario_steps'
    
    id = db.Column(db.Integer, primary_key=True)
    scenario_id = db.Column(db.Integer, db.ForeignKey('scenarios.id'), nullable=False)
    step_number = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(200))
    description = db.Column(db.Text)
    parameters = db.Column(db.Text)
    expected_outcome = db.Column(db.Text)
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}
    
    def set_parameters(self, params):
        self.parameters = json.dumps(params)