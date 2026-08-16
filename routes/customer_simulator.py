from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from database.models.customer import Customer
from database.models.company import Company

customer_bp = Blueprint('customer_simulator', __name__)

@customer_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    customers = Customer.query.filter_by(company_id=company_id).order_by(Customer.created_at.desc()).all()
    
    # FIX: Get company for realistic customer counts
    company = Company.query.get(company_id)
    
    # Calculate metrics from DB records or use company estimates
    total_customers = len(customers)
    active_customers = len([c for c in customers if c.status == 'active'])
    churned_customers = len([c for c in customers if getattr(c, 'is_churned', False)])
    
    # If no customer records in DB, use company settings for realistic display
    if total_customers == 0 and company:
        from services.analytics_service import AnalyticsService
        estimated_customers = AnalyticsService._estimate_customers(company)
        total_customers = estimated_customers
        active_customers = int(estimated_customers * 0.85)  # 85% active
        churned_customers = int(estimated_customers * 0.05)   # 5% churned
    
    return render_template('customer/customer_simulator.html', 
                         customers=customers,
                         company=company,
                         total_customers=total_customers,
                         active_customers=active_customers,
                         churned_customers=churned_customers)