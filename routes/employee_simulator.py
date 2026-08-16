from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from database.models.employee import Employee
from database.models.department import Department
from database.models.company import Company
from config.constants import CURRENCY_SYMBOLS

employee_bp = Blueprint('employee_simulator', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@employee_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    employees = Employee.query.filter_by(company_id=company_id).order_by(Employee.created_at.desc()).all()
    departments = Department.query.filter_by(company_id=company_id).all()
    
    # FIX: Get employee count from company settings (not just DB records)
    company = Company.query.get(company_id)
    total_employee_count = company.employee_count if company and company.employee_count else len(employees)
    
    return render_template('employee/employee_simulator.html', 
                         employees=employees, 
                         departments=departments,
                         total_employee_count=total_employee_count,
                         company=company,
                         currency_symbol=currency_symbol)