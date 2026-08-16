from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from database.models.financial import FinancialRecord, FinancialAccount
from database.models.loan import Loan
from database.models.investment import Investment
from database.models.company import Company
from services.analytics_service import AnalyticsService
from config.constants import CURRENCY_SYMBOLS

financial_bp = Blueprint('financial_modeling', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@financial_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    accounts = FinancialAccount.query.filter_by(company_id=company_id).all()
    recent_transactions = FinancialRecord.query.filter_by(company_id=company_id).order_by(
        FinancialRecord.transaction_date.desc()
    ).limit(50).all()
    summary = AnalyticsService.get_executive_summary(company_id)
    return render_template('financial/financial_modeling.html',
                         accounts=accounts, transactions=recent_transactions, summary=summary,
                         currency_symbol=currency_symbol)

@financial_bp.route('/investment')
@login_required
def investment():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    investments = Investment.query.filter_by(company_id=company_id).all()
    return render_template('financial/investment_simulator.html', investments=investments,
                         currency_symbol=currency_symbol)

@financial_bp.route('/expansion')
@login_required
def expansion():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    from database.models.branch import Branch
    branches = Branch.query.filter_by(company_id=company_id).all()
    return render_template('financial/expansion_simulator.html', branches=branches,
                         currency_symbol=currency_symbol)