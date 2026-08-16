import json
import ast
from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models.simulation import Simulation
from services.simulation_service import SimulationService
from config.constants import SIMULATION_TYPES, SIMULATION_LABELS, CURRENCY_SYMBOLS
from datetime import datetime

simulation_bp = Blueprint('simulation', __name__)


def _get_currency_symbol(company_id=None):
    """Fetch the company's currency symbol from session or database."""
    currency = session.get('company_currency')
    if not currency and company_id:
        from database.models.company import Company
        company = Company.query.get(company_id)
        if company:
            currency = company.currency
            session['company_currency'] = currency
            session['currency_symbol'] = CURRENCY_SYMBOLS.get(currency, '$')
    return CURRENCY_SYMBOLS.get(currency or 'USD', '$')


def _merge_sim_results(sim, sim_dict):
    """Merge parsed simulation results into the dict so frontend can access custom fields."""
    if sim.results:
        try:
            results_data = json.loads(sim.results)
            sim_dict.update(results_data)
        except Exception:
            try:
                results_data = ast.literal_eval(sim.results)
                sim_dict.update(results_data)
            except Exception:
                pass
    return sim_dict


@simulation_bp.route('/')
@login_required
def center():
    company_id = session.get('company_id')
    simulations = Simulation.query.filter_by(company_id=company_id).order_by(Simulation.created_at.desc()).limit(50).all()
    sim_configs = SimulationService.SIMULATION_CONFIGS
    currency_symbol = _get_currency_symbol(company_id)
    return render_template('simulation/simulation_center.html', 
                         simulations=simulations, 
                         sim_types=SIMULATION_TYPES,
                         sim_labels=SIMULATION_LABELS,
                         sim_configs=sim_configs,
                         currency_symbol=currency_symbol)


@simulation_bp.route('/run/<sim_type>', methods=['GET', 'POST'])
@login_required
def run_simulation(sim_type):
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol(company_id)

    if request.method == 'POST':
        name = request.form.get('name', f'{SIMULATION_LABELS.get(sim_type, "Simulation")} - {datetime.now().strftime("%Y-%m-%d %H:%M")}')
        params = {}

        config = SimulationService.SIMULATION_CONFIGS.get(sim_type, {})
        for input_field in config.get('inputs', []):
            val = request.form.get(input_field)
            if val:
                try:
                    if '.' in val:
                        params[input_field] = float(val)
                    else:
                        params[input_field] = int(val)
                except:
                    params[input_field] = val

        sim = SimulationService.run_simulation(company_id, current_user.id, sim_type, name, params, currency_symbol)

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            sim_dict = sim.to_dict()
            sim_dict = _merge_sim_results(sim, sim_dict)
            return jsonify({'success': True, 'simulation': sim_dict})

        flash('Simulation completed successfully!', 'success')
        return redirect(url_for('simulation.results', sim_id=sim.id))

    config = SimulationService.SIMULATION_CONFIGS.get(sim_type, {})

    # Get real data for the form
    real_data = {}
    if sim_type in ['price_increase', 'price_reduction', 'product_launch']:
        real_data['products'] = SimulationService._get_products_for_company(company_id)
    if sim_type in ['employee_hiring', 'employee_layoff']:
        real_data['departments'] = SimulationService._get_departments_for_company(company_id)
        real_data['roles'] = SimulationService._get_employee_roles(company_id)
        real_data['avg_salary'] = SimulationService._get_avg_salary(company_id)
    if sim_type in ['supplier_change']:
        real_data['suppliers'] = SimulationService._get_suppliers_for_company(company_id)

    # Get baseline for default values
    baseline = SimulationService._get_company_baseline(company_id)

    template_map = {
        'price_increase': 'simulation/price_simulation.html',
        'price_reduction': 'simulation/price_simulation.html',
        'new_branch': 'simulation/expansion_simulation.html',
        'employee_hiring': 'simulation/hiring_simulation.html',
        'employee_layoff': 'simulation/layoff_simulation.html',
        'inventory_expansion': 'simulation/inventory_simulation.html',
        'product_launch': 'simulation/product_launch.html',
        'marketing_campaign': 'simulation/marketing_simulation.html',
        'loan_taking': 'simulation/loan_simulation.html',
        'investment_planning': 'simulation/investment_simulation.html',
        'international_expansion': 'simulation/international_simulation.html',
        'warehouse_expansion': 'simulation/expansion_simulation.html',
        'supplier_change': 'simulation/supplier_simulation.html',
        'tax_changes': 'simulation/tax_simulation.html',
        'currency_fluctuation': 'simulation/currency_simulation.html',
        'inflation_impact': 'simulation/inflation_simulation.html',
        'market_crash': 'simulation/market_crash.html',
        'competitor_entry': 'simulation/competitor_simulation.html',
        'economic_recession': 'simulation/recession_simulation.html',
        'customer_growth': 'simulation/demand_simulation.html',
        'demand_growth': 'simulation/demand_simulation.html',
        'supply_disruption': 'simulation/disruption_simulation.html'
    }

    template = template_map.get(sim_type, 'simulation/simulation_center.html')
    return render_template(template, 
                         sim_type=sim_type, 
                         sim_label=SIMULATION_LABELS.get(sim_type, sim_type), 
                         config=config,
                         real_data=real_data,
                         baseline=baseline,
                         currency_symbol=currency_symbol,
                         now=datetime.now().strftime('%Y-%m-%d'))


@simulation_bp.route('/results/<int:sim_id>')
@login_required
def results(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    if sim.company_id != session.get('company_id'):
        flash('Access denied', 'danger')
        return redirect(url_for('simulation.center'))
    currency_symbol = _get_currency_symbol(session.get('company_id'))
    return render_template('simulation/simulation_center.html', simulation=sim, view_result=True, currency_symbol=currency_symbol)


@simulation_bp.route('/api/results/<int:sim_id>')
@login_required
def api_results(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    if sim.company_id != session.get('company_id'):
        return jsonify({'error': 'Access denied'}), 403
    sim_dict = sim.to_dict()
    sim_dict = _merge_sim_results(sim, sim_dict)
    return jsonify(sim_dict)


@simulation_bp.route('/save/<int:sim_id>', methods=['POST'])
@login_required
def save_simulation(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    sim.is_saved = True
    from database.db import db
    db.session.commit()
    return jsonify({'success': True})


@simulation_bp.route('/delete/<int:sim_id>', methods=['POST'])
@login_required
def delete_simulation(sim_id):
    sim = Simulation.query.get_or_404(sim_id)
    from database.db import db
    db.session.delete(sim)
    db.session.commit()
    return jsonify({'success': True})