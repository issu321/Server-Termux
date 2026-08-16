from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models.scenario import Scenario, ScenarioStep
from database.db import db

scenario_bp = Blueprint('scenario_builder', __name__)

@scenario_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    scenarios = Scenario.query.filter_by(company_id=company_id).order_by(Scenario.created_at.desc()).all()
    return render_template('scenario/scenario_builder.html', scenarios=scenarios)

@scenario_bp.route('/create', methods=['POST'])
@login_required
def create():
    company_id = session.get('company_id')
    scenario = Scenario(
        company_id=company_id,
        user_id=current_user.id,
        name=request.form.get('name'),
        description=request.form.get('description'),
        scenario_type=request.form.get('scenario_type')
    )
    db.session.add(scenario)
    db.session.commit()
    flash('Scenario created!', 'success')
    return redirect(url_for('scenario_builder.index'))