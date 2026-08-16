from flask import Blueprint, render_template, jsonify, session, redirect, request
from flask_login import login_required, current_user
from database.models.company import Company
from database.models.simulation import Simulation
from database.models.forecast import Forecast
from database.models.risk import Risk
from database.models.notification import Notification
from database.models.activity_log import ActivityLog
from database.db import db
from services.analytics_service import AnalyticsService
from services.risk_service import RiskService
from config.constants import CURRENCY_SYMBOLS
from datetime import datetime
from zoneinfo import ZoneInfo

dashboard_bp = Blueprint('dashboard', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@dashboard_bp.route('/')
@dashboard_bp.route('/dashboard')
@login_required
def index():
    company_id = session.get('company_id')
    if not company_id:
        return redirect('/logout')
    
    currency_symbol = _get_currency_symbol()
    company = Company.query.get(company_id)
    summary = AnalyticsService.get_executive_summary(company_id)
    risk_summary = RiskService.get_risk_summary(company_id)
    trend_data = AnalyticsService.get_trend_data(company_id, 90)
    dept_performance = AnalyticsService.get_department_performance(company_id)
    
    # Override employee count from company settings
    if company and company.employee_count:
        summary['total_employees'] = company.employee_count
    
    # Override customer count from company settings
    if company and hasattr(company, 'customer_count') and company.customer_count:
        summary['total_customers'] = company.customer_count
    
    # Get company timezone for live clock
    company_timezone = 'UTC'
    if company and company.timezone:
        company_timezone = company.timezone
    try:
        local_now = datetime.now(ZoneInfo(company_timezone))
    except Exception:
        local_now = datetime.utcnow()
        company_timezone = 'UTC'
    
    # Recent activities
    activities = ActivityLog.query.filter_by(company_id=company_id).order_by(
        ActivityLog.created_at.desc()
    ).limit(10).all()
    
    # Recent simulations
    simulations = Simulation.query.filter_by(company_id=company_id).order_by(
        Simulation.created_at.desc()
    ).limit(5).all()
    
    # Recent forecasts
    forecasts = Forecast.query.filter_by(company_id=company_id).order_by(
        Forecast.created_at.desc()
    ).limit(5).all()
    
    # Notifications
    notifications = Notification.query.filter_by(
        company_id=company_id, 
        user_id=current_user.id,
        is_read=False
    ).order_by(Notification.created_at.desc()).limit(5).all()
    
    return render_template('dashboard.html',
                         company=company,
                         summary=summary,
                         risk_summary=risk_summary,
                         trend_data=trend_data,
                         dept_performance=dept_performance,
                         activities=activities,
                         simulations=simulations,
                         forecasts=forecasts,
                         notifications=notifications,
                         currency_symbol=currency_symbol,
                         company_timezone=company_timezone,
                         local_now=local_now)

@dashboard_bp.route('/api/metrics')
@login_required
def api_metrics():
    company_id = session.get('company_id')
    company = Company.query.get(company_id)
    summary = AnalyticsService.get_executive_summary(company_id)
    risk_summary = RiskService.get_risk_summary(company_id)
    
    employee_count = company.employee_count if company and company.employee_count else summary.get('total_employees', 0)
    customer_count = company.customer_count if company and hasattr(company, 'customer_count') and company.customer_count else summary.get('total_customers', 0)
    
    return jsonify({
        'health_score': summary['health_score'],
        'revenue_30d': summary['revenue_30d'],
        'profit_30d': summary['profit_30d'],
        'margin': summary['margin'],
        'risk_score': risk_summary['overall_score'],
        'total_customers': customer_count,
        'churn_rate': summary['churn_rate'],
        'employees': employee_count
    })

@dashboard_bp.route('/api/chart-data')
@login_required
def chart_data():
    company_id = session.get('company_id')
    days = int(request.args.get('days', 90))
    trend = AnalyticsService.get_trend_data(company_id, days)
    return jsonify(trend)

# ─── TIMEZONE UPDATE ROUTE ───
@dashboard_bp.route('/api/update-timezone', methods=['POST'])
@login_required
def update_timezone():
    try:
        company_id = session.get('company_id')
        if not company_id:
            return jsonify({'success': False, 'error': 'Not authenticated'}), 401
        
        company = Company.query.get(company_id)
        if not company:
            return jsonify({'success': False, 'error': 'Company not found'}), 404
        
        data = request.get_json(force=True, silent=True) or {}
        new_tz = data.get('timezone', 'UTC')
        
        # Validate timezone
        try:
            ZoneInfo(new_tz)
        except Exception:
            return jsonify({'success': False, 'error': 'Invalid timezone: ' + new_tz}), 400
        
        # Save to database
        company.timezone = new_tz
        db.session.commit()
        
        return jsonify({'success': True, 'timezone': new_tz})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500