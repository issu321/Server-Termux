from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from database.models.department import Department
from database.models.employee import Employee
from database.models.financial import FinancialRecord
from database.models.company import Company
from database.db import db
from sqlalchemy import func
from datetime import datetime, timedelta
from config.constants import CURRENCY_SYMBOLS

operations_bp = Blueprint('operations_simulator', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@operations_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    departments_raw = Department.query.filter_by(company_id=company_id, is_active=True).all()
    
    # Department colors for consistent UI
    dept_colors = {
        'Sales': '#10b981', 'Marketing': '#f59e0b', 'Operations': '#3b82f6',
        'Finance': '#8b5cf6', 'HR': '#ec4899', 'IT': '#06b6d4',
        'Engineering': '#6366f1', 'Product': '#14b8a6', 'Legal': '#64748b',
        'Support': '#84cc16', 'R&D': '#f97316', 'Admin': '#94a3b8'
    }
    
    departments = []
    total_budget = 0
    total_spent = 0
    total_employees = 0
    
    start_of_year = datetime.utcnow().replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    
    for dept in departments_raw:
        # Count active employees in this department
        emp_count = db.session.query(func.count(Employee.id)).filter(
            Employee.department_id == dept.id,
            Employee.company_id == company_id,
            Employee.status == 'active'
        ).scalar() or 0
        
        # Calculate payroll cost (sum of active employee salaries)
        payroll = db.session.query(func.sum(Employee.salary)).filter(
            Employee.department_id == dept.id,
            Employee.company_id == company_id,
            Employee.status == 'active',
            Employee.salary.isnot(None)
        ).scalar() or 0.0
        
        # Calculate other departmental expenses from financial records
        other_expenses = db.session.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.company_id == company_id,
            FinancialRecord.department_id == dept.id,
            FinancialRecord.transaction_type == 'expense',
            FinancialRecord.transaction_date >= start_of_year.date()
        ).scalar() or 0.0
        
        total_spent_dept = float(payroll) + float(other_expenses)
        budget = float(dept.budget or 0)
        if budget <= 0:
            # Fallback: if no budget set, estimate as payroll * 1.2 or 100k
            budget = max(total_spent_dept * 1.2, 100000)
        
        utilization = (total_spent_dept / budget * 100) if budget > 0 else 0
        remaining = budget - total_spent_dept
        
        # Color based on utilization
        if utilization > 95:
            bar_color = '#ef4444'  # Red - critical
            status = 'Over Budget'
        elif utilization > 80:
            bar_color = '#f59e0b'  # Yellow - warning
            status = 'High Utilization'
        elif utilization > 50:
            bar_color = '#3b82f6'  # Blue - normal
            status = 'On Track'
        else:
            bar_color = '#10b981'  # Green - healthy
            status = 'Healthy'
        
        # Cost per employee
        cost_per_emp = total_spent_dept / max(emp_count, 1)
        
        # Budget headroom months (if spending continues at current rate)
        months_active = max((datetime.utcnow().month - 1), 1)
        monthly_burn = total_spent_dept / max(months_active, 1)
        runway_months = remaining / max(monthly_burn, 1) if monthly_burn > 0 else 12
        
        departments.append({
            'id': dept.id,
            'name': dept.name,
            'code': dept.code or dept.name[:3].upper(),
            'employee_count': emp_count,
            'budget': budget,
            'spent': total_spent_dept,
            'payroll': float(payroll),
            'other_expenses': float(other_expenses),
            'remaining': remaining,
            'utilization': utilization,
            'utilization_display': min(utilization, 100),  # Cap bar at 100%
            'bar_color': bar_color,
            'status': status,
            'cost_per_employee': cost_per_emp,
            'runway_months': runway_months,
            'color': dept_colors.get(dept.name, '#667eea')
        })
        
        total_budget += budget
        total_spent += total_spent_dept
        total_employees += emp_count
    
    # Sort by utilization (highest first) to surface problems
    departments.sort(key=lambda x: x['utilization'], reverse=True)
    
    overall_utilization = (total_spent / total_budget * 100) if total_budget > 0 else 0
    overall_remaining = total_budget - total_spent
    
    summary = {
        'total_departments': len(departments),
        'total_employees': total_employees,
        'total_budget': total_budget,
        'total_spent': total_spent,
        'total_remaining': overall_remaining,
        'overall_utilization': overall_utilization,
        'avg_cost_per_employee': total_spent / max(total_employees, 1)
    }
    
    return render_template('operations/operations_simulator.html', 
                         departments=departments, 
                         summary=summary,
                         currency_symbol=currency_symbol)