from flask import Blueprint, render_template, jsonify, session, request
from flask_login import login_required
from services.analytics_service import AnalyticsService
from database.models.analytics import Analytics
from config.constants import CURRENCY_SYMBOLS

analytics_bp = Blueprint('analytics', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or fallback to CURRENCY_SYMBOLS."""
    if 'currency_symbol' in session:
        return session['currency_symbol']
    currency = session.get('company_currency', 'USD')
    return CURRENCY_SYMBOLS.get(currency, '$')

@analytics_bp.route('/')
@login_required
def overview():
    company_id = session.get('company_id')
    summary = AnalyticsService.get_executive_summary(company_id)
    trend = AnalyticsService.get_trend_data(company_id, 90)
    dept_perf = AnalyticsService.get_department_performance(company_id)
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/analytics_overview.html',
                         summary=summary, trend=trend, dept_perf=dept_perf,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/revenue')
@login_required
def revenue():
    company_id = session.get('company_id')
    trend = AnalyticsService.get_trend_data(company_id, 180)
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/revenue_analytics.html', trend=trend,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/expenses')
@login_required
def expenses():
    company_id = session.get('company_id')
    dept_perf = AnalyticsService.get_department_performance(company_id)
    summary = AnalyticsService.get_executive_summary(company_id)
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/expense_analytics.html', dept_perf=dept_perf, summary=summary,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/profit')
@login_required
def profit():
    company_id = session.get('company_id')
    trend = AnalyticsService.get_trend_data(company_id, 365)
    summary = AnalyticsService.get_executive_summary(company_id)
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/profit_analytics.html', trend=trend, summary=summary,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/growth')
@login_required
def growth():
    company_id = session.get('company_id')
    summary = AnalyticsService.get_executive_summary(company_id)
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/growth_analytics.html', summary=summary,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/departments')
@login_required
def departments():
    company_id = session.get('company_id')
    dept_perf = AnalyticsService.get_department_performance(company_id)
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/department_analytics.html', dept_perf=dept_perf,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/customers')
@login_required
def customers():
    company_id = session.get('company_id')
    from database.models.customer import Customer
    customers = Customer.query.filter_by(company_id=company_id).all()
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/customer_analytics.html', customers=customers,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/employees')
@login_required
def employees():
    company_id = session.get('company_id')
    from database.models.employee import Employee
    employees = Employee.query.filter_by(company_id=company_id).all()
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/employee_analytics.html', employees=employees,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/supply-chain')
@login_required
def supply_chain():
    company_id = session.get('company_id')
    from database.models.supplier import Supplier
    suppliers = Supplier.query.filter_by(company_id=company_id).all()
    currency_symbol = _get_currency_symbol()
    return render_template('analytics/supply_chain_analytics.html', suppliers=suppliers,
                         currency_symbol=currency_symbol)

@analytics_bp.route('/api/trend')
@login_required
def api_trend():
    company_id = session.get('company_id')
    days = int(request.args.get('days', 90))
    currency_symbol = _get_currency_symbol()
    data = AnalyticsService.get_trend_data(company_id, days)
    data['currency_symbol'] = currency_symbol
    return jsonify(data)