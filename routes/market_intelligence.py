from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required
from database.models.market_data import MarketData
from database.models.company import Company
from services.market_intelligence_service import MarketIntelligenceService
from database.db import db
from config.constants import CURRENCY_SYMBOLS

market_bp = Blueprint('market_intelligence', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@market_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    currency_code = session.get('company_currency', 'USD')
    
    # Auto-generate benchmarks if empty, then fetch summary
    summary = MarketIntelligenceService.get_market_summary(company_id, currency_code=currency_code)
    market_data = summary['data'] if summary else []
    
    return render_template('market/market_intelligence.html', 
                         market_data=market_data,
                         summary=summary,
                         currency_symbol=currency_symbol)

@market_bp.route('/refresh', methods=['POST'])
@login_required
def refresh():
    company_id = session.get('company_id')
    currency_code = session.get('company_currency', 'USD')
    MarketIntelligenceService.refresh_market_data(company_id, currency_code=currency_code)
    flash('Market intelligence data refreshed with latest industry benchmarks.', 'success')
    return redirect(url_for('market_intelligence.index'))

@market_bp.route('/import', methods=['POST'])
@login_required
def import_data():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    # Simple CSV/JSON import via textarea
    import json
    raw = request.form.get('import_data', '').strip()
    if not raw:
        flash('No data provided.', 'warning')
        return redirect(url_for('market_intelligence.index'))
    
    try:
        records = json.loads(raw)
        if isinstance(records, dict):
            records = [records]
        MarketIntelligenceService.import_market_data(company_id, records)
        flash(f'Imported {len(records)} market data records.', 'success')
    except Exception as e:
        flash(f'Import failed: {str(e)}', 'danger')
    
    return redirect(url_for('market_intelligence.index'))

@market_bp.route('/api/data')
@login_required
def api_data():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    summary = MarketIntelligenceService.get_market_summary(company_id)
    return jsonify({
        'summary': {k: v for k, v in summary.items() if k != 'data'} if summary else None,
        'records': [d.to_dict() for d in (summary['data'] if summary else [])],
        'currency_symbol': currency_symbol
    })