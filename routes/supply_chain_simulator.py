from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from database.models.supplier import Supplier
from database.models.inventory import Inventory, InventoryMovement
from database.models.company import Company
from config.constants import CURRENCY_SYMBOLS

supply_chain_bp = Blueprint('supply_chain_simulator', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@supply_chain_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    suppliers = Supplier.query.filter_by(company_id=company_id).all()
    items = Inventory.query.filter_by(company_id=company_id, is_active=True).all()
    return render_template('supply_chain/supply_chain_simulator.html', 
                         suppliers=suppliers, 
                         items=items,
                         currency_symbol=currency_symbol)