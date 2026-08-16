from database.db import db
from datetime import datetime

class AppConfig(db.Model):
    __tablename__ = 'app_config'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'))
    config_key = db.Column(db.String(100), nullable=False)
    config_value = db.Column(db.Text)
    config_type = db.Column(db.String(20), default='string')
    description = db.Column(db.String(255))
    is_encrypted = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('company_id', 'config_key', name='uq_config_key'),)
    
    @staticmethod
    def get(company_id, key, default=None):
        config = AppConfig.query.filter_by(company_id=company_id, config_key=key).first()
        return config.config_value if config else default
    
    @staticmethod
    def set(company_id, key, value, config_type='string'):
        config = AppConfig.query.filter_by(company_id=company_id, config_key=key).first()
        if config:
            config.config_value = str(value)
            config.config_type = config_type
        else:
            config = AppConfig(company_id=company_id, config_key=key, 
                             config_value=str(value), config_type=config_type)
            db.session.add(config)
        db.session.commit()
        return config
    
    def to_dict(self):
        return {
            'id': self.id,
            'config_key': self.config_key,
            'config_value': self.config_value,
            'config_type': self.config_type,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }