from database.db import db
from datetime import datetime
import json

class Forecast(db.Model):
    __tablename__ = 'forecasts'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    forecast_type = db.Column(db.String(50), nullable=False)
    method = db.Column(db.String(50), default='prophet')
    horizon_days = db.Column(db.Integer, default=90)
    status = db.Column(db.String(20), default='running')
    parameters = db.Column(db.Text)
    accuracy_mae = db.Column(db.Float)
    accuracy_rmse = db.Column(db.Float)
    accuracy_mape = db.Column(db.Float)
    accuracy_r2 = db.Column(db.Float)
    summary = db.Column(db.Text)
    is_saved = db.Column(db.Boolean, default=False)
    schedule = db.Column(db.String(20), default='manual')
    last_run = db.Column(db.DateTime)
    next_run = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = db.relationship('User', backref='forecasts')
    results = db.relationship('ForecastResult', backref='forecast', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_parameters(self):
        return json.loads(self.parameters) if self.parameters else {}
    
    def set_parameters(self, params):
        self.parameters = json.dumps(params)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'forecast_type': self.forecast_type,
            'method': self.method,
            'horizon_days': self.horizon_days,
            'status': self.status,
            'accuracy_mae': self.accuracy_mae,
            'accuracy_rmse': self.accuracy_rmse,
            'accuracy_mape': self.accuracy_mape,
            'accuracy_r2': self.accuracy_r2,
            'schedule': self.schedule,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class ForecastResult(db.Model):
    __tablename__ = 'forecast_results'
    
    id = db.Column(db.Integer, primary_key=True)
    forecast_id = db.Column(db.Integer, db.ForeignKey('forecasts.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    value = db.Column(db.Float)
    lower_bound = db.Column(db.Float)
    upper_bound = db.Column(db.Float)
    actual = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)