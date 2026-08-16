from database.db import db
from datetime import datetime

class CompanyPayments(db.Model):
    __tablename__ = 'company_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    qr_code_path = db.Column(db.String(255))
    upi_link = db.Column(db.String(500))
    upi_id = db.Column(db.String(200))
    bank_transfer_details = db.Column(db.Text)
    bank_account_number = db.Column(db.String(100))
    bank_ifsc = db.Column(db.String(50))
    bank_name = db.Column(db.String(200))
    payment_gateway_link = db.Column(db.String(500))
    payment_link = db.Column(db.String(500))
    stripe_key = db.Column(db.String(500))
    paypal_link = db.Column(db.String(500))
    razorpay_key = db.Column(db.String(500))
    whatsapp_business_link = db.Column(db.String(500))
    telegram_business_link = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'qr_code_path': self.qr_code_path,
            'upi_link': self.upi_link,
            'upi_id': self.upi_id,
            'bank_transfer_details': self.bank_transfer_details,
            'bank_account_number': self.bank_account_number,
            'bank_ifsc': self.bank_ifsc,
            'bank_name': self.bank_name,
            'payment_gateway_link': self.payment_gateway_link,
            'payment_link': self.payment_link,
            'whatsapp_business_link': self.whatsapp_business_link,
            'telegram_business_link': self.telegram_business_link
        }