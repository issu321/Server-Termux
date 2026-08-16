from flask import Blueprint, render_template, request, jsonify, session, flash
from flask_login import login_required, current_user
from database.models.risk import Risk, RiskFactor
from services.risk_service import RiskService
from config.constants import RISK_CATEGORIES, RISK_LABELS
from database.db import db

risk_engine_bp = Blueprint('risk_engine', __name__)

@risk_engine_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    risks = RiskService.assess_all_risks(company_id)
    summary = RiskService.get_risk_summary(company_id)
    
    # FIX: Convert risks to dicts in Python, not in Jinja template
    risks_data = [r.to_dict() for r in risks]
    
    risks_by_category = {}
    for cat in RISK_CATEGORIES:
        risks_by_category[cat] = [r for r in risks if r.category == cat]
    
    return render_template('risk/risk_engine.html',
                         risks=risks, 
                         summary=summary,
                         categories=RISK_CATEGORIES,
                         category_labels=RISK_LABELS,
                         risks_by_category=risks_by_category,
                         risks_data=risks_data)

@risk_engine_bp.route('/heatmap')
@login_required
def heatmap():
    company_id = session.get('company_id')
    risks = Risk.query.filter_by(company_id=company_id).all()
    heatmap_data = [{
        'name': r.name,
        'probability': r.probability,
        'impact': r.impact,
        'score': r.risk_score,
        'level': r.risk_level
    } for r in risks]
    return render_template('risk/risk_heatmap.html', heatmap_data=heatmap_data)

@risk_engine_bp.route('/api/assess', methods=['POST'])
@login_required
def api_assess():
    company_id = session.get('company_id')
    summary = RiskService.get_risk_summary(company_id)
    return jsonify(summary)

@risk_engine_bp.route('/create', methods=['POST'])
@login_required
def create_risk():
    company_id = session.get('company_id')
    risk = Risk(
        company_id=company_id,
        name=request.form.get('name'),
        category=request.form.get('category'),
        description=request.form.get('description'),
        probability=float(request.form.get('probability', 0.5)),
        impact=float(request.form.get('impact', 0.5)),
        mitigation_plan=request.form.get('mitigation_plan'),
        owner_id=current_user.id
    )
    risk.calculate_score()
    db.session.add(risk)
    db.session.commit()
    flash('Risk assessment created!', 'success')
    return jsonify({'success': True, 'risk': risk.to_dict()})