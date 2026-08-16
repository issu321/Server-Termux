from database.db import db
from datetime import datetime
import json

class Simulation(db.Model):
    __tablename__ = 'simulations'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    sim_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='running')
    parameters = db.Column(db.Text)
    results = db.Column(db.Text)
    revenue_before = db.Column(db.Float, default=0.0)
    revenue_after = db.Column(db.Float, default=0.0)
    cost_before = db.Column(db.Float, default=0.0)
    cost_after = db.Column(db.Float, default=0.0)
    profit_before = db.Column(db.Float, default=0.0)
    profit_after = db.Column(db.Float, default=0.0)
    risk_score = db.Column(db.Float)
    confidence_low = db.Column(db.Float)
    confidence_high = db.Column(db.Float)
    recommendations = db.Column(db.Text)
    is_saved = db.Column(db.Boolean, default=False)
    is_shared = db.Column(db.Boolean, default=False)
    share_token = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='simulations')
    params = db.relationship('SimulationParam', backref='simulation', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}
    
    def set_parameters(self, params):
        self.parameters = json.dumps(params)
    
    def get_results(self):
        return json.loads(self.results) if self.results else {}
    
    def set_results(self, results):
        self.results = json.dumps(results)
    
    def to_dict(self):
        # Start with base fields stored in DB columns
        data = {
            'id': self.id,
            'name': self.name,
            'sim_type': self.sim_type,
            'status': self.status,
            'revenue_before': self.revenue_before or 0,
            'revenue_after': self.revenue_after or 0,
            'cost_before': self.cost_before or 0,
            'cost_after': self.cost_after or 0,
            'profit_before': self.profit_before or 0,
            'profit_after': self.profit_after or 0,
            'risk_score': self.risk_score or 0,
            'confidence_low': self.confidence_low,
            'confidence_high': self.confidence_high,
            'recommendations': self.recommendations or '',
            'is_saved': self.is_saved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
        
        # Merge custom calculation results (annual_cost, productivity_gain, roi_pct, etc.)
        try:
            result_data = self.get_results()
            if result_data and isinstance(result_data, dict):
                for key, value in result_data.items():
                    if key not in data:
                        data[key] = value
        except Exception:
            pass
        
        return data

class SimulationParam(db.Model):
    __tablename__ = 'simulation_params'
    
    id = db.Column(db.Integer, primary_key=True)
    simulation_id = db.Column(db.Integer, db.ForeignKey('simulations.id'), nullable=False)
    param_name = db.Column(db.String(100), nullable=False)
    param_value = db.Column(db.String(500))
    param_type = db.Column(db.String(20), default='string')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)