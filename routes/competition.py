from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required
from database.models.competitor import Competitor
from services.competition_service import CompetitionService
from database.db import db

competition_bp = Blueprint('competition', __name__)

@competition_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    summary = CompetitionService.get_competition_summary(company_id)
    competitors = summary['competitors'] if summary else []
    
    return render_template('market/competition_analysis.html', 
                         competitors=competitors,
                         summary=summary)

@competition_bp.route('/refresh', methods=['POST'])
@login_required
def refresh():
    company_id = session.get('company_id')
    CompetitionService.refresh_competitors(company_id)
    flash('Competitor landscape refreshed with latest market intelligence.', 'success')
    return redirect(url_for('competition.index'))

@competition_bp.route('/api/summary')
@login_required
def api_summary():
    company_id = session.get('company_id')
    summary = CompetitionService.get_competition_summary(company_id)
    if not summary:
        return jsonify({'error': 'No data available'}), 404
    
    # Remove non-serializable objects
    data = {k: v for k, v in summary.items() if k != 'competitors' and k != 'market_leader'}
    data['competitors'] = [{
        'name': c.name,
        'threat_level': c.threat_level,
        'market_share': c.market_share,
        'revenue_estimate': c.revenue_estimate,
        'employee_count': c.employee_count,
        'market_position': c.market_position
    } for c in summary['competitors']]
    data['market_leader'] = {
        'name': summary['market_leader'].name,
        'market_share': summary['market_leader'].market_share,
        'revenue_estimate': summary['market_leader'].revenue_estimate
    } if summary.get('market_leader') else None
    
    return jsonify(data)