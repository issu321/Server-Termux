from database.db import db
from datetime import datetime

class MarketingCampaign(db.Model):
    __tablename__ = 'marketing_campaigns'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    campaign_type = db.Column(db.String(50))
    channel = db.Column(db.String(100))
    status = db.Column(db.String(20), default='draft')
    budget = db.Column(db.Float, default=0.0)
    spent = db.Column(db.Float, default=0.0)
    target_audience = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    impressions = db.Column(db.Integer, default=0)
    clicks = db.Column(db.Integer, default=0)
    conversions = db.Column(db.Integer, default=0)
    revenue_generated = db.Column(db.Float, default=0.0)
    roi = db.Column(db.Float)
    cpa = db.Column(db.Float)
    ctr = db.Column(db.Float)
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def calculate_roi(self):
        if self.spent > 0 and self.revenue_generated > 0:
            self.roi = ((self.revenue_generated - self.spent) / self.spent) * 100
        return self.roi
    
    def calculate_ctr(self):
        if self.impressions > 0 and self.clicks > 0:
            self.ctr = (self.clicks / self.impressions) * 100
        return self.ctr
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'campaign_type': self.campaign_type,
            'channel': self.channel,
            'status': self.status,
            'budget': self.budget,
            'spent': self.spent,
            'impressions': self.impressions,
            'clicks': self.clicks,
            'conversions': self.conversions,
            'revenue_generated': self.revenue_generated,
            'roi': self.roi,
            'ctr': self.ctr,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }