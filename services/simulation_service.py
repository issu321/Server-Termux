import os
import json
from database.db import db
from database.models.simulation import Simulation, SimulationParam
from services.company_service import CompanyService
from datetime import datetime, timedelta
import numpy as np


class SimulationService:
    SIMULATION_CONFIGS = {
        'price_increase': {
            'inputs': ['current_price', 'new_price', 'product_name', 'market_segment', 'elasticity'],
            'calculation': 'price_elasticity'
        },
        'price_reduction': {
            'inputs': ['current_price', 'discount_percent', 'duration_months', 'target_segment'],
            'calculation': 'discount_impact'
        },
        'new_branch': {
            'inputs': ['location', 'rent_monthly', 'staff_count', 'setup_cost', 'expected_customers'],
            'calculation': 'branch_expansion'
        },
        'employee_hiring': {
            'inputs': ['role', 'salary', 'benefits', 'department', 'start_date'],
            'calculation': 'hiring_cost'
        },
        'employee_layoff': {
            'inputs': ['headcount_reduction', 'avg_severance', 'departments', 'notice_period'],
            'calculation': 'layoff_savings'
        },
        'inventory_expansion': {
            'inputs': ['new_skus', 'quantity_per_sku', 'unit_cost', 'warehouse_cost'],
            'calculation': 'inventory_cost'
        },
        'product_launch': {
            'inputs': ['product_name', 'rd_cost', 'marketing_budget', 'launch_months', 'target_market_size'],
            'calculation': 'launch_projections'
        },
        'marketing_campaign': {
            'inputs': ['channel', 'budget', 'duration_days', 'target_audience', 'expected_ctr'],
            'calculation': 'campaign_roi'
        },
        'loan_taking': {
            'inputs': ['amount', 'interest_rate', 'tenure_months', 'purpose'],
            'calculation': 'loan_impact'
        },
        'investment_planning': {
            'inputs': ['amount', 'return_rate', 'risk_level', 'timeline_months', 'investment_type'],
            'calculation': 'investment_returns'
        },
        'international_expansion': {
            'inputs': ['target_country', 'market_size', 'entry_mode', 'investment', 'local_partners'],
            'calculation': 'international_roi'
        },
        'warehouse_expansion': {
            'inputs': ['location', 'size_sqft', 'monthly_cost', 'automation_level', 'staff_count'],
            'calculation': 'warehouse_roi'
        },
        'supplier_change': {
            'inputs': ['current_cost', 'new_cost', 'quality_rating', 'lead_time', 'transition_cost'],
            'calculation': 'supplier_savings'
        },
        'tax_changes': {
            'inputs': ['current_rate', 'new_rate', 'tax_type', 'affected_revenue'],
            'calculation': 'tax_impact'
        },
        'currency_fluctuation': {
            'inputs': ['currency_pair', 'rate_change_percent', 'exposure_amount'],
            'calculation': 'currency_impact'
        },
        'inflation_impact': {
            'inputs': ['inflation_rate', 'duration_months', 'affected_costs'],
            'calculation': 'inflation_effect'
        },
        'market_crash': {
            'inputs': ['severity', 'duration_months', 'affected_sectors'],
            'calculation': 'crash_scenario'
        },
        'competitor_entry': {
            'inputs': ['competitor_type', 'target_segment', 'pricing_strategy', 'marketing_spend'],
            'calculation': 'competitive_response'
        },
        'economic_recession': {
            'inputs': ['severity', 'duration_months', 'industry_impact'],
            'calculation': 'recession_impact'
        },
        'customer_growth': {
            'inputs': ['growth_rate', 'acquisition_channels', 'retention_improvement'],
            'calculation': 'growth_projection'
        },
        'demand_growth': {
            'inputs': ['demand_increase_percent', 'product_lines', 'seasonality_factor'],
            'calculation': 'demand_capacity'
        },
        'supply_disruption': {
            'inputs': ['disruption_type', 'duration_weeks', 'affected_suppliers', 'backup_available'],
            'calculation': 'disruption_impact'
        }
    }

    @staticmethod
    def _fmt_money(amount, currency_symbol='$'):
        """Format a number with the company's currency symbol. No sign."""
        try:
            val = float(amount) if amount is not None else 0
            return f"{currency_symbol}{abs(val):,.0f}"
        except (ValueError, TypeError):
            return f"{currency_symbol}0"

    @staticmethod
    def _fmt_signed(amount, currency_symbol='$'):
        """Format a signed number: +₹1,234 or -₹1,234."""
        try:
            val = float(amount) if amount is not None else 0
            sign = '+' if val >= 0 else '-'
            return f"{sign}{currency_symbol}{abs(val):,.0f}"
        except (ValueError, TypeError):
            return f"{currency_symbol}0"

    @staticmethod
    def run_simulation(company_id, user_id, sim_type, name, parameters, currency_symbol='$'):
        config = SimulationService.SIMULATION_CONFIGS.get(sim_type, {})

        sim = Simulation(
            company_id=company_id,
            user_id=user_id,
            name=name,
            sim_type=sim_type,
            status='running',
            parameters=str(parameters)
        )
        db.session.add(sim)
        db.session.commit()

        try:
            calculator = getattr(SimulationService, f"_calc_{config.get('calculation', 'default')}", SimulationService._calc_default)
            results = calculator(company_id, parameters, currency_symbol)

            sim.status = 'completed'
            sim.revenue_before = results.get('revenue_before', 0)
            sim.revenue_after = results.get('revenue_after', 0)
            sim.cost_before = results.get('cost_before', 0)
            sim.cost_after = results.get('cost_after', 0)
            sim.profit_before = results.get('profit_before', 0)
            sim.profit_after = results.get('profit_after', 0)
            sim.risk_score = results.get('risk_score', 50)
            sim.confidence_low = results.get('confidence_low')
            sim.confidence_high = results.get('confidence_high')
            sim.recommendations = results.get('recommendations', '')
            sim.results = json.dumps(results)

        except Exception as e:
            sim.status = 'failed'
            sim.recommendations = f"Error: {str(e)}"

        db.session.commit()
        return sim

    @staticmethod
    def _get_company_baseline(company_id):
        company = CompanyService.get_company(company_id)
        if not company:
            return {'revenue': 1000000, 'costs': 700000, 'profit': 300000, 'employees': 50, 'customers': 100}

        from database.models.financial import FinancialRecord
        from sqlalchemy import func

        end_date = datetime.utcnow().date()
        start_date = (datetime.utcnow() - timedelta(days=365)).date()

        annual_revenue = db.session.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.company_id == company_id,
            FinancialRecord.transaction_type == 'revenue',
            FinancialRecord.transaction_date >= start_date,
            FinancialRecord.transaction_date <= end_date
        ).scalar() or 0

        annual_cost = db.session.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.company_id == company_id,
            FinancialRecord.transaction_type == 'expense',
            FinancialRecord.transaction_date >= start_date,
            FinancialRecord.transaction_date <= end_date
        ).scalar() or 0

        if annual_revenue == 0:
            annual_revenue = company.annual_revenue or 1000000
        if annual_cost == 0:
            annual_cost = (company.annual_revenue * 0.7) if company.annual_revenue else 700000

        # ===== SANITY CHECK: Prevent fake-looking margins (>90% or negative) =====
        if annual_revenue > 0:
            calculated_margin = (annual_revenue - annual_cost) / annual_revenue
            if calculated_margin > 0.90 or calculated_margin <= 0:
                annual_cost = annual_revenue * 0.80
        # ========================================================================

        from database.models.employee import Employee
        employee_count = db.session.query(func.count(Employee.id)).filter(
            Employee.company_id == company_id,
            Employee.status == 'active'
        ).scalar() or company.employee_count or 50

        from database.models.customer import Customer
        customer_count = db.session.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.status == 'active',
            Customer.is_churned == False
        ).scalar() or company.customer_count or 100

        from database.models.inventory import Inventory
        inventory_items = Inventory.query.filter_by(company_id=company_id, is_active=True).all()
        total_inventory_value = sum(item.stock_value() for item in inventory_items)
        low_stock_count = sum(1 for item in inventory_items if item.is_low_stock())

        products = []
        for item in inventory_items[:5]:
            products.append({
                'name': item.name,
                'price': item.selling_price or 0,
                'cost': item.unit_cost or 0,
                'quantity': item.quantity_on_hand or 0
            })

        revenue_per_customer = annual_revenue / max(customer_count, 1) if customer_count > 0 else 1000
        revenue_per_customer = min(max(revenue_per_customer, 50), 50000)

        return {
            'revenue': float(annual_revenue),
            'costs': float(annual_cost),
            'profit': float(annual_revenue - annual_cost),
            'employees': employee_count,
            'customers': customer_count,
            'revenue_per_customer': revenue_per_customer,
            'inventory_value': float(total_inventory_value),
            'low_stock_count': low_stock_count,
            'products': products,
            'company': company
        }

    @staticmethod
    def _get_products_for_company(company_id):
        from database.models.inventory import Inventory
        items = Inventory.query.filter_by(company_id=company_id, is_active=True).all()
        if not items:
            return [{'name': 'Default Product', 'price': 100.0, 'cost': 60.0, 'quantity': 500}]
        return [{
            'name': item.name,
            'price': item.selling_price or 100.0,
            'cost': item.unit_cost or 60.0,
            'quantity': item.quantity_on_hand or 0,
            'sku': item.sku
        } for item in items]

    @staticmethod
    def _get_departments_for_company(company_id):
        from database.models.employee import Employee
        from sqlalchemy import func
        depts = db.session.query(Employee.department_id).filter(
            Employee.company_id == company_id,
            Employee.department_id.isnot(None)
        ).distinct().all()
        from database.models.department import Department
        dept_names = []
        for d in depts:
            dept = Department.query.get(d[0])
            if dept:
                dept_names.append(dept.name)
        return dept_names or ['Sales', 'Marketing', 'Engineering', 'Operations', 'HR']

    @staticmethod
    def _get_employee_roles(company_id):
        from database.models.employee import Employee
        from sqlalchemy import func
        roles = db.session.query(Employee.job_title).filter(
            Employee.company_id == company_id,
            Employee.job_title.isnot(None)
        ).distinct().all()
        return [r[0] for r in roles if r[0]] or ['Manager', 'Developer', 'Sales Rep', 'Analyst']

    @staticmethod
    def _get_avg_salary(company_id):
        from database.models.employee import Employee
        from sqlalchemy import func
        avg = db.session.query(func.avg(Employee.salary)).filter(
            Employee.company_id == company_id,
            Employee.status == 'active',
            Employee.salary.isnot(None)
        ).scalar()
        return float(avg) if avg else 50000.0

    @staticmethod
    def _get_suppliers_for_company(company_id):
        from database.models.supplier import Supplier
        suppliers = Supplier.query.filter_by(company_id=company_id).all()
        return suppliers or []

    @staticmethod
    def _calc_price_elasticity(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        products = baseline['products']

        product_name = params.get('product_name', products[0]['name'] if products else 'Product')
        product = next((p for p in products if p['name'] == product_name), products[0] if products else {'price': 100, 'cost': 60, 'quantity': 500})

        current_price = float(params.get('current_price', product['price'])) if product['price'] > 0 else 100.0
        new_price = float(params.get('new_price', current_price * 1.1))
        elasticity = float(params.get('elasticity', -1.5))

        price_change_pct = (new_price - current_price) / current_price if current_price > 0 else 0
        volume_change_pct = elasticity * price_change_pct

        baseline_volume = product['quantity'] or (baseline['revenue'] / max(current_price, 1) / 12)
        new_volume = max(baseline_volume * (1 + volume_change_pct), 0)

        revenue_before = current_price * baseline_volume
        revenue_after = new_price * new_volume

        unit_cost = product['cost'] or (current_price * 0.6)
        cost_before = unit_cost * baseline_volume
        cost_after = unit_cost * new_volume

        profit_before = revenue_before - cost_before
        profit_after = revenue_after - cost_after

        churn_risk = min(abs(price_change_pct) * 100 * 2, 30)
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        return {
            'revenue_before': round(revenue_before, 2),
            'revenue_after': round(revenue_after, 2),
            'cost_before': round(cost_before, 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 30 + churn_risk,
            'confidence_low': round(revenue_after * 0.85, 2),
            'confidence_high': round(revenue_after * 1.15, 2),
            'volume_change_pct': round(volume_change_pct * 100, 2),
            'price_change_pct': round(price_change_pct * 100, 2),
            'churn_risk': round(churn_risk, 2),
            'product_name': product_name,
            'recommendations': f"Price change of {round(price_change_pct*100,1)}% on '{product_name}' results in {round(volume_change_pct*100,1)}% volume change. Revenue: {fmt(revenue_after, cs)} vs {fmt(revenue_before, cs)}. Monitor customer churn closely."
        }

    @staticmethod
    def _calc_discount_impact(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        discount = float(params.get('discount_percent', 10)) / 100
        duration = int(params.get('duration_months', 3))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        monthly_revenue = baseline['revenue'] / 12
        volume_boost = discount * 3
        revenue_during = monthly_revenue * (1 + volume_boost) * (1 - discount)
        revenue_normal = monthly_revenue

        avg_monthly_revenue = (revenue_during * duration + revenue_normal * (12 - duration)) / 12
        cost_after = (baseline['costs'] / 12) * (1 + volume_boost * 0.4)

        profit_before = baseline['profit']
        profit_after = (avg_monthly_revenue * 12) - (cost_after * 12)
        net_impact = avg_monthly_revenue * 12 - baseline['revenue']

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(avg_monthly_revenue * 12, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(cost_after * 12, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 25 + discount * 100,
            'confidence_low': round(avg_monthly_revenue * 12 * 0.8, 2),
            'confidence_high': round(avg_monthly_revenue * 12 * 1.2, 2),
            'volume_boost_pct': round(volume_boost * 100, 2),
            'discount_amount': round(discount * 100, 1),
            'recommendations': f"Discount of {discount*100:.0f}% boosts volume by ~{round(volume_boost*100)}% but reduces margin by {discount*100:.0f}%. Net revenue impact: {signed(net_impact, cs)}/year."
        }

    @staticmethod
    def _calc_branch_expansion(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        rent = float(params.get('rent_monthly', 5000))
        staff = int(params.get('staff_count', 5))
        setup = float(params.get('setup_cost', 50000))
        customers_per_month = int(params.get('expected_customers', 100))
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        annual_customers = customers_per_month * 12
        revenue_per_customer = baseline.get('revenue_per_customer', 1000)
        new_revenue = annual_customers * revenue_per_customer

        avg_salary = SimulationService._get_avg_salary(company_id)
        annual_cost = rent * 12 + staff * avg_salary + setup
        monthly_cost = annual_cost / 12

        break_even_months = setup / max((new_revenue - annual_cost) / 12, 1) if new_revenue > annual_cost else float('inf')

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + new_revenue - annual_cost

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + new_revenue, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + annual_cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 40 if new_revenue > annual_cost else 65,
            'confidence_low': round(new_revenue * 0.6, 2),
            'confidence_high': round(new_revenue * 1.4, 2),
            'break_even_months': round(break_even_months, 1) if break_even_months != float('inf') else 'Never',
            'annual_cost': round(annual_cost, 2),
            'new_revenue': round(new_revenue, 2),
            'recommendations': f"New branch adds {fmt(new_revenue, cs)}/yr revenue ({customers_per_month} customers/mo x {fmt(revenue_per_customer, cs)}) with {fmt(annual_cost, cs)} annual cost. Break-even: {round(break_even_months, 1) if break_even_months != float('inf') else 'Never'} months."
        }

    @staticmethod
    def _calc_hiring_cost(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        salary = float(params.get('salary', SimulationService._get_avg_salary(company_id)))
        benefits = float(params.get('benefits', salary * 0.3))
        role = params.get('role', 'Employee')
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        total_cost = salary + benefits
        role_multipliers = {'manager': 3.0, 'developer': 2.8, 'sales': 3.5, 'analyst': 2.5, 'marketing': 2.7}
        role_key = role.lower().split()[0] if role else 'employee'
        multiplier = role_multipliers.get(role_key, 2.5)
        productivity_gain = total_cost * multiplier

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + productivity_gain - total_cost

        roi = ((productivity_gain - total_cost) / total_cost * 100) if total_cost > 0 else 0

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + productivity_gain, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + total_cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 20,
            'annual_cost': round(total_cost, 2),
            'productivity_gain': round(productivity_gain, 2),
            'roi_pct': round(roi, 1),
            'recommendations': f"Hiring {role} at {fmt(salary, cs)}/yr (total cost: {fmt(total_cost, cs)}). Expected productivity value: {fmt(productivity_gain, cs)}. ROI: {round(roi)}%."
        }

    @staticmethod
    def _calc_layoff_savings(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        reduction = int(params.get('headcount_reduction', 1))
        severance = float(params.get('avg_severance', SimulationService._get_avg_salary(company_id) * 0.5))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        avg_cost_per_employee = baseline['costs'] / max(baseline['employees'], 1)
        annual_savings = reduction * avg_cost_per_employee
        severance_cost = reduction * severance
        morale_impact = min(reduction / max(baseline['employees'], 1) * 30, 25) if baseline['employees'] > 0 else 0

        revenue_loss = baseline['revenue'] * (morale_impact / 100)
        cost_after = baseline['costs'] - annual_savings

        profit_before = baseline['profit']
        profit_after = baseline['revenue'] - revenue_loss - cost_after
        net_first = annual_savings - severance_cost

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] - revenue_loss, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 50 + morale_impact,
            'annual_savings': round(annual_savings, 2),
            'severance_cost': round(severance_cost, 2),
            'morale_impact': round(morale_impact, 2),
            'net_first_year': round(net_first, 2),
            'recommendations': f"Layoff {reduction} employees saves {fmt(annual_savings, cs)}/yr but costs {fmt(severance_cost, cs)} in severance. Morale impact: {round(morale_impact)}%. Net first year: {signed(net_first, cs)}. Consider alternatives."
        }

    @staticmethod
    def _calc_inventory_cost(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        new_skus = int(params.get('new_skus', 5))
        qty_per_sku = int(params.get('quantity_per_sku', 100))
        unit_cost = float(params.get('unit_cost', 50))
        warehouse_cost = float(params.get('warehouse_cost', 2000))
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        total_inventory_cost = new_skus * qty_per_sku * unit_cost
        annual_cost = warehouse_cost * 12 + total_inventory_cost

        selling_price = unit_cost * 1.4
        new_revenue = new_skus * qty_per_sku * selling_price * 2

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + new_revenue - annual_cost

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + new_revenue, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + annual_cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 35,
            'inventory_investment': round(total_inventory_cost, 2),
            'annual_cost': round(annual_cost, 2),
            'new_revenue': round(new_revenue, 2),
            'recommendations': f"Expand inventory by {new_skus} SKUs ({new_skus * qty_per_sku} units). Investment: {fmt(total_inventory_cost, cs)}. Expected new revenue: {fmt(new_revenue, cs)}/yr. ROI: {round((new_revenue - annual_cost) / total_inventory_cost * 100) if total_inventory_cost > 0 else 0}%."
        }

    @staticmethod
    def _calc_launch_projections(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        rd_cost = float(params.get('rd_cost', 100000))
        marketing = float(params.get('marketing_budget', 50000))
        months = int(params.get('launch_months', 6))
        market_size = int(params.get('target_market_size', 10000))
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        total_cost = rd_cost + marketing + (baseline['costs'] * 0.05 * months / 12)

        penetration = min(0.02 + (marketing / 100000) * 0.03, 0.08)
        new_customers = market_size * penetration
        revenue_per_customer = baseline.get('revenue_per_customer', 1000)
        new_revenue = new_customers * revenue_per_customer

        year1_revenue = new_revenue * 0.4
        year2_revenue = new_revenue * 0.8

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + year1_revenue - total_cost

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + year1_revenue, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + total_cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 55,
            'total_investment': round(total_cost, 2),
            'year1_revenue': round(year1_revenue, 2),
            'year2_revenue': round(year2_revenue, 2),
            'market_penetration': round(penetration * 100, 1),
            'recommendations': f"Launch requires {fmt(total_cost, cs)} investment. Year 1 revenue: {fmt(year1_revenue, cs)}, Year 2: {fmt(year2_revenue, cs)}. Market penetration: {round(penetration*100,1)}%. Break-even likely in month {round(total_cost / max(year1_revenue/12, 1))}."
        }

    @staticmethod
    def _calc_campaign_roi(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        budget = float(params.get('budget', 10000))
        duration = int(params.get('duration_days', 30))
        ctr = float(params.get('expected_ctr', 2.5)) / 100
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        impressions = budget * 100
        clicks = impressions * ctr
        conversion_rate = 0.05
        conversions = clicks * conversion_rate

        revenue_per_customer = baseline.get('revenue_per_customer', 1000)
        new_revenue = conversions * revenue_per_customer
        cost = budget

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + new_revenue - cost

        roi = ((new_revenue - cost) / cost * 100) if cost > 0 else 0

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + new_revenue, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 30,
            'impressions': round(impressions, 0),
            'clicks': round(clicks, 0),
            'conversions': round(conversions, 0),
            'roi_pct': round(roi, 1),
            'cost_per_acquisition': round(cost / max(conversions, 1), 2),
            'recommendations': f"Campaign reaches {impressions:,.0f} impressions, {clicks:,.0f} clicks, {conversions:,.0f} conversions. Revenue: {fmt(new_revenue, cs)}. ROI: {roi:.0f}%. CPA: {fmt(cost / max(conversions, 1), cs)}."
        }

    @staticmethod
    def _calc_loan_impact(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        amount = float(params.get('amount', 100000))
        rate = float(params.get('interest_rate', 8)) / 100
        tenure = int(params.get('tenure_months', 60))
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        monthly_rate = rate / 12
        if monthly_rate > 0:
            emi = amount * monthly_rate * (1 + monthly_rate)**tenure / ((1 + monthly_rate)**tenure - 1)
        else:
            emi = amount / tenure

        total_payment = emi * tenure
        total_interest = total_payment - amount

        revenue_boost = amount * 0.15
        annual_emi = emi * 12

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + revenue_boost - annual_emi

        total_equity = baseline.get('total_equity', 100000.0)
        existing_debt = baseline.get('total_existing_debt', 0.0)
        total_debt = existing_debt + amount

        debt_equity = total_debt / max(total_equity, 1.0)

        monthly_cash_flow = max(baseline['profit'] / 12.0, 1.0)
        emi_to_cashflow_pct = (emi / monthly_cash_flow) * 100.0 if monthly_cash_flow > 0 else 0.0

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + revenue_boost, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + annual_emi, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': min(30 + debt_equity * 20, 80),
            'emi_monthly': round(emi, 2),
            'total_interest': round(total_interest, 2),
            'total_payment': round(total_payment, 2),
            'debt_equity_ratio': round(debt_equity, 4),
            'total_debt': round(total_debt, 2),
            'total_equity': round(total_equity, 2),
            'monthly_cash_flow': round(monthly_cash_flow, 2),
            'emi_to_cashflow_pct': round(emi_to_cashflow_pct, 2),
            'recommendations': f"EMI: {fmt(emi, cs)}/month. Total interest: {fmt(total_interest, cs)}. Debt/Equity: {debt_equity:.4f}. Total debt: {fmt(total_debt, cs)} on {fmt(total_equity, cs)} equity. EMI is {emi_to_cashflow_pct:.2f}% of monthly cash flow ({fmt(monthly_cash_flow, cs)})."
        }

    @staticmethod
    def _calc_investment_returns(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        amount = float(params.get('amount', 100000))
        return_rate = float(params.get('return_rate', 10)) / 100
        timeline = int(params.get('timeline_months', 12))
        risk = params.get('risk_level', 'medium')
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        risk_adjustment = {'low': 0.02, 'medium': 0, 'high': -0.03}
        adj_return = return_rate + risk_adjustment.get(risk, 0)
        years = timeline / 12
        future_value = amount * (1 + adj_return) ** years

        profit_before = baseline['profit']
        profit_after = baseline['profit']

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'], 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'], 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 30 if risk == 'low' else 50 if risk == 'medium' else 70,
            'future_value': round(future_value, 2),
            'total_return': round(future_value - amount, 2),
            'return_pct': round((future_value - amount) / amount * 100, 2) if amount > 0 else 0,
            'annualized_return': round(adj_return * 100, 1),
            'recommendations': f"Investment of {fmt(amount, cs)} grows to {fmt(future_value, cs)} in {timeline} months ({risk} risk). Annualized return: {adj_return*100:.1f}%. Diversify to minimize risk."
        }

    @staticmethod
    def _calc_international_roi(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        target_country = params.get('target_country', 'New Market')
        market_size = int(params.get('market_size', 50000))
        entry_mode = params.get('entry_mode', 'partnership')
        investment = float(params.get('investment', 200000))
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        entry_factors = {'partnership': 0.15, 'franchise': 0.12, 'wholly_owned': 0.08, 'export': 0.05}
        penetration = entry_factors.get(entry_mode, 0.1)

        new_customers = market_size * penetration

        domestic_rpu = baseline.get('revenue_per_customer', 1000)
        revenue_per_customer = min(domestic_rpu * 0.3, 500.0)

        new_revenue = new_customers * revenue_per_customer

        annual_cost = investment * 0.4 + new_revenue * 0.3

        annual_net = new_revenue - annual_cost
        monthly_net = annual_net / 12.0

        if monthly_net > 0:
            break_even = (investment / monthly_net)
            break_even = max(break_even, 6.0)
        else:
            break_even = float('inf')

        if break_even == float('inf'):
            break_even_display = 'Never'
        elif break_even > 120:
            break_even_display = '> 10 years'
        else:
            break_even_display = round(break_even, 1)

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + new_revenue - annual_cost

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + new_revenue, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + annual_cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 55 if entry_mode == 'partnership' else 70,
            'new_revenue': round(new_revenue, 2),
            'investment': round(investment, 2),
            'break_even_months': break_even_display,
            'market_penetration': round(penetration * 100, 1),
            'recommendations': f"Enter {target_country} via {entry_mode}. Investment: {fmt(investment, cs)}. Expected revenue: {fmt(new_revenue, cs)}. Break-even: {break_even_display} months. Currency and regulatory risks apply."
        }

    @staticmethod
    def _calc_warehouse_roi(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        size_sqft = int(params.get('size_sqft', 10000))
        monthly_cost = float(params.get('monthly_cost', 8000))
        automation = params.get('automation_level', 'medium')
        staff = int(params.get('staff_count', 3))
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        automation_savings = {'low': 0.05, 'medium': 0.15, 'high': 0.25}
        efficiency_gain = automation_savings.get(automation, 0.15)

        current_logistics_cost = baseline['costs'] * 0.15
        savings = current_logistics_cost * efficiency_gain

        avg_salary = SimulationService._get_avg_salary(company_id)
        annual_cost = monthly_cost * 12 + staff * avg_salary
        new_revenue = savings * 2

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + new_revenue + savings - annual_cost

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + new_revenue, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + annual_cost - savings, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 35,
            'annual_cost': round(annual_cost, 2),
            'efficiency_savings': round(savings, 2),
            'roi_years': round(annual_cost / max(savings, 1), 1) if savings > 0 else 'N/A',
            'recommendations': f"Warehouse ({size_sqft:,} sqft) with {automation} automation saves {fmt(savings, cs)}/yr. Annual cost: {fmt(annual_cost, cs)}. ROI period: {round(annual_cost / max(savings, 1), 1) if savings > 0 else 'N/A'} years."
        }

    @staticmethod
    def _calc_supplier_savings(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        current_cost = float(params.get('current_cost', 100))
        new_cost = float(params.get('new_cost', 85))
        quality = params.get('quality_rating', 'same')
        lead_time = int(params.get('lead_time', 14))
        transition = float(params.get('transition_cost', 5000))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        from database.models.inventory import Inventory
        items = Inventory.query.filter_by(company_id=company_id, is_active=True).all()
        annual_volume = sum(item.quantity_on_hand for item in items) * 4

        cost_diff = (current_cost - new_cost) * annual_volume
        quality_risk = {'better': -5, 'same': 0, 'worse': 15, 'unknown': 10}
        risk_adjustment = quality_risk.get(quality, 0)

        net_savings = cost_diff - transition
        profit_before = baseline['profit']
        profit_after = baseline['profit'] + net_savings

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'], 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] - net_savings, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 25 + risk_adjustment + (5 if lead_time > 21 else 0),
            'annual_savings': round(cost_diff, 2),
            'net_savings': round(net_savings, 2),
            'payback_months': round(transition / max(cost_diff / 12, 1), 1) if cost_diff > 0 else 'N/A',
            'recommendations': f"Switching suppliers saves {fmt(cost_diff, cs)}/yr. Transition cost: {fmt(transition, cs)}. Net savings: {fmt(net_savings, cs)}. Quality risk: {quality}. Lead time: {lead_time} days."
        }

    # ============ TAX CHANGES - COMPLETELY REWRITTEN FOR ACCURACY ============
    @staticmethod
    def _calc_tax_impact(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        current_rate = float(params.get('current_rate', 25)) / 100
        new_rate = float(params.get('new_rate', 28)) / 100
        tax_type = params.get('tax_type', 'corporate')
        affected_revenue = float(params.get('affected_revenue', 0))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        # Get company's actual financials
        actual_revenue = baseline['revenue']
        actual_costs = baseline['costs']
        actual_profit = baseline['profit']

        # Calculate actual margin from real data
        if actual_revenue > 0:
            actual_margin = actual_profit / actual_revenue
        else:
            actual_margin = 0.20

        # SANITY CHECK: If margin is unrealistic (>90% or negative), 
        # fall back to a realistic 20% default to prevent fake-looking results
        if actual_margin > 0.90 or actual_margin <= 0:
            actual_margin = 0.20

        # Determine which revenue to use for the simulation
        if affected_revenue > 0:
            sim_revenue = affected_revenue
        else:
            sim_revenue = actual_revenue

        # Calculate costs and profit for the simulation using the validated margin
        sim_costs = sim_revenue * (1 - actual_margin)
        sim_profit = sim_revenue * actual_margin

        # Determine taxable base based on tax type
        if tax_type in ['sales', 'vat']:
            # Sales tax / VAT is applied to REVENUE directly
            tax_on_profit = False
            taxable_base = sim_revenue
            applied_margin = 1.0

            # Tax is treated as a cost for sales/VAT
            current_tax = taxable_base * current_rate
            new_tax = taxable_base * new_rate
            tax_diff = new_tax - current_tax

            revenue_before = sim_revenue
            revenue_after = sim_revenue
            cost_before = sim_costs + current_tax
            cost_after = sim_costs + new_tax
            profit_before = sim_profit - current_tax
            profit_after = sim_profit - new_tax

        else:
            # Corporate / Income tax is applied to PROFIT (taxable income)
            tax_on_profit = True
            taxable_base = sim_profit
            applied_margin = actual_margin

            # Calculate taxes
            current_tax = taxable_base * current_rate
            new_tax = taxable_base * new_rate
            tax_diff = new_tax - current_tax

            # For corporate tax: costs don't change, profit is after-tax
            revenue_before = sim_revenue
            revenue_after = sim_revenue
            cost_before = sim_costs
            cost_after = sim_costs
            profit_before = taxable_base - current_tax
            profit_after = taxable_base - new_tax

        # Ensure no negative values
        taxable_base = max(taxable_base, 0)
        current_tax = max(current_tax, 0)
        new_tax = max(new_tax, 0)

        return {
            'revenue_before': round(revenue_before, 2),
            'revenue_after': round(revenue_after, 2),
            'cost_before': round(cost_before, 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 30,
            'current_tax': round(current_tax, 2),
            'new_tax': round(new_tax, 2),
            'tax_diff': round(tax_diff, 2),
            'effective_rate': round(new_rate * 100, 1),
            'taxable_base': round(taxable_base, 2),
            'taxable_income': round(taxable_base, 2),
            'profit_margin_pct': round(applied_margin * 100, 2),
            'actual_margin_pct': round(actual_margin * 100, 2),
            'tax_on_profit': tax_on_profit,
            'recommendations': f"{tax_type.title()} tax rate change from {current_rate*100:.0f}% to {new_rate*100:.0f}%. Taxable base: {fmt(taxable_base, cs)} (margin: {applied_margin*100:.1f}%). Tax at {current_rate*100:.0f}%: {fmt(current_tax, cs)}. Tax at {new_rate*100:.0f}%: {fmt(new_tax, cs)}. Additional tax: {signed(tax_diff, cs)}/yr. After-tax profit at {current_rate*100:.0f}%: {fmt(profit_before, cs)}. After-tax profit at {new_rate*100:.0f}%: {fmt(profit_after, cs)}."
        }

    # ============ CURRENCY FLUCTUATION - FIXED WITH PURE PYTHON ============
    @staticmethod
    def _calc_currency_impact(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        pair = params.get('currency_pair', 'USD/EUR')
        rate_change = float(params.get('rate_change_percent', 5)) / 100
        exposure = float(params.get('exposure_amount', baseline['revenue'] * 0.3))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        # Pair volatility multipliers - different pairs have different risk levels
        pair_volatility = {
            'USD/EUR': 1.0,
            'USD/GBP': 1.1,
            'USD/CAD': 0.8,
            'USD/AUD': 1.1,
            'USD/CNY': 0.9,
            'USD/INR': 1.2,
            'USD/JPY': 1.3,
            'EUR/GBP': 0.7,
            'EUR/JPY': 1.4,
            'GBP/JPY': 1.5
        }
        volatility = pair_volatility.get(pair, 1.0)
        effective_rate_change = rate_change * volatility

        # Realistic exposure split: 60% revenue-linked, 40% cost-linked
        revenue_exposure = exposure * 0.6
        cost_exposure = exposure * 0.4

        # Calculate impacts
        revenue_impact = revenue_exposure * effective_rate_change
        cost_impact = cost_exposure * effective_rate_change
        net_profit_impact = revenue_impact - cost_impact

        direction = 'favorable' if effective_rate_change > 0 else 'unfavorable'

        revenue_before = baseline['revenue']
        revenue_after = baseline['revenue'] + revenue_impact
        cost_before = baseline['costs']
        cost_after = baseline['costs'] + cost_impact
        profit_before = baseline['profit']
        profit_after = baseline['profit'] + net_profit_impact

        # Risk based on exposure % of revenue AND pair volatility
        exposure_pct = (exposure / max(baseline['revenue'], 1)) * 100
        risk_score = min(30 + exposure_pct * 0.5 * volatility, 85)

        recommendations = (
            f"{pair} {direction} by {abs(effective_rate_change)*100:.1f}% (volatility: {volatility}x). "
            f"Revenue exposure ({fmt(revenue_exposure, cs)}) impact: {signed(revenue_impact, cs)}. "
            f"Cost exposure ({fmt(cost_exposure, cs)}) impact: {signed(cost_impact, cs)}. "
            f"Net profit impact: {signed(net_profit_impact, cs)}. "
            f"Total exposure is {exposure_pct:.1f}% of annual revenue. "
            f"Consider hedging with forward contracts or options."
        )

        return {
            'revenue_before': round(revenue_before, 2),
            'revenue_after': round(revenue_after, 2),
            'cost_before': round(cost_before, 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': round(risk_score, 0),
            'impact_amount': round(net_profit_impact, 2),
            'revenue_impact': round(revenue_impact, 2),
            'cost_impact': round(cost_impact, 2),
            'exposure': round(exposure, 2),
            'revenue_exposure': round(revenue_exposure, 2),
            'cost_exposure': round(cost_exposure, 2),
            'direction': direction,
            'rate_change_pct': round(rate_change * 100, 1),
            'effective_rate_change_pct': round(effective_rate_change * 100, 1),
            'volatility': round(volatility, 1),
            'pair': pair,
            'recommendations': recommendations
        }

    # ============ INFLATION IMPACT ============
    @staticmethod
    def _calc_inflation_effect(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        inflation = float(params.get('inflation_rate', 3)) / 100
        duration = int(params.get('duration_months', 12))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        cumulative = (1 + inflation) ** (duration / 12) - 1
        cost_increase = baseline['costs'] * cumulative
        revenue_adjustment = baseline['revenue'] * cumulative * 0.5

        profit_before = baseline['profit']
        profit_after = baseline['profit'] - cost_increase + revenue_adjustment
        net_impact = revenue_adjustment - cost_increase

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + revenue_adjustment, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + cost_increase, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 35 + inflation * 500,
            'cost_increase': round(cost_increase, 2),
            'revenue_adjustment': round(revenue_adjustment, 2),
            'cumulative_inflation': round(cumulative * 100, 1),
            'recommendations': f"Inflation of {inflation*100:.1f}% over {duration} months increases costs by {fmt(cost_increase, cs)}. Can pass {fmt(revenue_adjustment, cs)} to customers. Net profit impact: {signed(net_impact, cs)}."
        }

    # ============ MARKET CRASH ============
    @staticmethod
    def _calc_crash_scenario(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        severity = params.get('severity', 'moderate')
        duration = int(params.get('duration_months', 6))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        severity_multipliers = {'mild': 0.15, 'moderate': 0.35, 'severe': 0.6}
        revenue_drop = severity_multipliers.get(severity, 0.35)

        revenue_loss = baseline['revenue'] * revenue_drop
        cost_savings = baseline['costs'] * revenue_drop * 0.3
        net_impact = revenue_loss - cost_savings

        recovery_months = duration * (2 if severity == 'mild' else 3 if severity == 'moderate' else 5)

        profit_before = baseline['profit']
        profit_after = baseline['profit'] - net_impact

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] - revenue_loss, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] - cost_savings, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 70 if severity == 'severe' else 55,
            'revenue_loss': round(revenue_loss, 2),
            'cost_savings': round(cost_savings, 2),
            'net_impact': round(net_impact, 2),
            'recovery_months': recovery_months,
            'recommendations': f"{severity.title()} crash: Revenue drops {revenue_drop*100:.0f}% ({fmt(revenue_loss, cs)}). Cost cuts save {fmt(cost_savings, cs)}. Net impact: {fmt(net_impact, cs)}. Recovery: {recovery_months} months. Build cash reserves."
        }

    # ============ COMPETITOR ENTRY ============
    @staticmethod
    def _calc_competitive_response(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        competitor_type = params.get('competitor_type', 'new_startup')
        segment = params.get('target_segment', 'all')
        pricing = params.get('pricing_strategy', 'aggressive')
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        share_loss = {'aggressive': 0.15, 'moderate': 0.08, 'premium': 0.05}.get(pricing, 0.1)
        if competitor_type == 'major_corporation':
            share_loss *= 1.5

        revenue_loss = baseline['revenue'] * share_loss
        defensive_spend = baseline['revenue'] * 0.03

        # Cost savings from lost revenue (variable costs only)
        cost_ratio = baseline['costs'] / baseline['revenue'] if baseline['revenue'] > 0 else 0.7
        cost_ratio = min(max(cost_ratio, 0.5), 0.95)
        variable_cost_ratio = cost_ratio * 0.6
        cost_savings = revenue_loss * variable_cost_ratio

        cost_after = baseline['costs'] - cost_savings + defensive_spend
        revenue_after = baseline['revenue'] - revenue_loss
        profit_after = revenue_after - cost_after
        profit_before = baseline['profit']
        net_profit = profit_after - profit_before

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(revenue_after, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 60 if competitor_type == 'major_corporation' else 45,
            'market_share_loss': round(share_loss * 100, 1),
            'revenue_loss': round(revenue_loss, 2),
            'defensive_spend': round(defensive_spend, 2),
            'cost_savings': round(cost_savings, 2),
            'recommendations': f"{competitor_type.replace('_', ' ').title()} entering {segment} with {pricing} pricing. Lose {share_loss*100:.1f}% market share ({fmt(revenue_loss, cs)} revenue). Defensive spend: {fmt(defensive_spend, cs)}. Variable cost savings: {fmt(cost_savings, cs)}. Net profit impact: {signed(net_profit, cs)}. Invest in differentiation or customer retention."
        }

    # ============ ECONOMIC RECESSION ============
    @staticmethod
    def _calc_recession_impact(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        severity = params.get('severity', 'moderate')
        duration = int(params.get('duration_months', 12))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        impacts = {'mild': 0.1, 'moderate': 0.25, 'severe': 0.45}
        revenue_drop = impacts.get(severity, 0.25)

        industry = baseline['company'].industry if baseline.get('company') else 'technology'
        resilient = industry in ['healthcare', 'utilities', 'education'] if industry else False
        if resilient:
            revenue_drop *= 0.5

        revenue_loss = baseline['revenue'] * revenue_drop
        cost_reduction = baseline['costs'] * revenue_drop * 0.4
        net_impact = revenue_loss - cost_reduction

        profit_before = baseline['profit']
        profit_after = baseline['profit'] - revenue_loss + cost_reduction

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] - revenue_loss, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] - cost_reduction, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 65 if severity == 'severe' else 50,
            'revenue_loss': round(revenue_loss, 2),
            'cost_reduction': round(cost_reduction, 2),
            'net_impact': round(net_impact, 2),
            'recommendations': f"{severity.title()} recession: Revenue drops {revenue_drop*100:.0f}% ({fmt(revenue_loss, cs)}). Cost cuts: {fmt(cost_reduction, cs)}. Net: {signed(net_impact, cs)}. Focus on cash flow and essential operations."
        }

    # ============ CUSTOMER GROWTH ============
    @staticmethod
    def _calc_growth_projection(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        growth_rate = float(params.get('growth_rate', 10)) / 100
        channels = params.get('acquisition_channels', 'organic')
        retention = float(params.get('retention_improvement', 5)) / 100
        cs = currency_symbol
        fmt = SimulationService._fmt_money

        current_customers = baseline['customers']
        new_customers = current_customers * growth_rate
        retained_customers = current_customers * (1 + retention)

        revenue_per_customer = baseline.get('revenue_per_customer', 1000)
        new_revenue = new_customers * revenue_per_customer
        retention_value = retained_customers * revenue_per_customer * retention

        cac_rates = {'organic': 50, 'paid': 200, 'referral': 80, 'partnership': 150, 'all': 120}
        cac = cac_rates.get(channels, 120)
        acquisition_cost = new_customers * cac

        profit_before = baseline['profit']
        profit_after = baseline['profit'] + new_revenue + retention_value - acquisition_cost

        ltv = revenue_per_customer * 3
        ltv_ratio = ltv / max(cac, 1)

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] + new_revenue + retention_value, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] + acquisition_cost, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 25,
            'new_customers': round(new_customers, 0),
            'acquisition_cost': round(acquisition_cost, 2),
            'cac': round(cac, 0),
            'ltv_ratio': round(ltv_ratio, 1),
            'recommendations': f"Growth of {growth_rate*100:.0f}% adds {new_customers:,.0f} customers at {fmt(cac, cs)} CAC. LTV/CAC: {ltv_ratio:.1f}x. Retention improvement worth {fmt(retention_value, cs)}."
        }

    # ============ DEMAND GROWTH - FIXED ============
    @staticmethod
    def _calc_demand_capacity(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        demand_increase = float(params.get('demand_increase_percent', 20)) / 100
        product_lines = int(params.get('product_lines', 3))
        seasonality = float(params.get('seasonality_factor', 1.0))
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        current_revenue = baseline['revenue']
        current_costs = baseline['costs']
        current_profit = baseline['profit']

        # Calculate actual cost ratio from baseline (prevents fake 100% profit margins)
        cost_ratio = current_costs / current_revenue if current_revenue > 0 else 0.7
        profit_margin = current_profit / current_revenue if current_revenue > 0 else 0.3

        # Clamp to realistic bounds
        cost_ratio = min(max(cost_ratio, 0.5), 0.95)
        profit_margin = min(max(profit_margin, 0.05), 0.5)

        # Calculate new demand value
        new_demand_value = current_revenue * demand_increase * seasonality

        # Capacity analysis (30% headroom above current revenue)
        capacity_limit = current_revenue * 1.3
        capacity_headroom = capacity_limit - current_revenue
        can_meet = new_demand_value <= capacity_headroom

        # Product line complexity factor (more lines = slightly higher variable costs)
        complexity_factor = 1 + ((product_lines - 1) * 0.02)

        if can_meet:
            expansion_cost = 0
            captured_revenue = new_demand_value
            capacity_gap = 0
        else:
            capacity_gap = new_demand_value - capacity_headroom
            captured_revenue = capacity_headroom
            # Expansion cost to close the gap (equipment, hiring, facilities)
            expansion_cost = capacity_gap * 0.5

        # Variable costs scale with additional revenue captured, adjusted for complexity
        additional_variable_costs = captured_revenue * cost_ratio * complexity_factor

        # Total costs after simulation
        cost_after = current_costs + additional_variable_costs + expansion_cost

        # Revenue after simulation
        revenue_after = current_revenue + captured_revenue

        # Profit after simulation (only margin on new revenue, minus expansion costs)
        profit_after = current_profit + captured_revenue - additional_variable_costs - expansion_cost
        net_profit_impact = captured_revenue - additional_variable_costs - expansion_cost

        # Risk score based on capacity utilization and expansion need
        utilization_after = (current_revenue + captured_revenue) / capacity_limit if capacity_limit > 0 else 0
        risk_score = 25 + (utilization_after * 25) + (30 if not can_meet else 0)
        risk_score = min(max(risk_score, 10), 95)

        return {
            'revenue_before': round(current_revenue, 2),
            'revenue_after': round(revenue_after, 2),
            'cost_before': round(current_costs, 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(current_profit, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': round(risk_score, 0),
            'demand_increase': round(demand_increase * 100, 1),
            'product_lines': product_lines,
            'seasonality_factor': seasonality,
            'new_demand': round(new_demand_value, 2),
            'captured_revenue': round(captured_revenue, 2),
            'capacity_limit': round(capacity_limit, 2),
            'capacity_headroom': round(capacity_headroom, 2),
            'capacity_gap': round(capacity_gap, 2),
            'expansion_needed': not can_meet,
            'expansion_cost': round(expansion_cost, 2),
            'additional_variable_costs': round(additional_variable_costs, 2),
            'cost_ratio': round(cost_ratio * 100, 1),
            'profit_margin': round(profit_margin * 100, 1),
            'complexity_factor': round(complexity_factor, 2),
            'recommendations': (
                f"Demand increases {demand_increase*100:.0f}% (seasonality factor: {seasonality}x). "
                f"New demand value: {fmt(new_demand_value, cs)}. "
                f"Capacity headroom: {fmt(capacity_headroom, cs)} (limit: {fmt(capacity_limit, cs)}). "
                f"Can meet demand: {'Yes' if can_meet else 'No'}. "
                f"Capacity gap: {fmt(capacity_gap, cs)}. "
                f"Expansion cost: {fmt(expansion_cost, cs)}. "
                f"Variable costs on new revenue: {fmt(additional_variable_costs, cs)} ({cost_ratio*100:.1f}% base cost ratio × {complexity_factor:.2f} complexity). "
                f"Net profit impact: {signed(net_profit_impact, cs)}. "
                + ("Invest in capacity expansion to capture unmet demand." if not can_meet else "Current capacity sufficient for demand spike.")
            )
        }

    # ============ SUPPLY DISRUPTION - FIXED ============
    @staticmethod
    def _calc_disruption_impact(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        disruption_type = params.get('disruption_type', 'supplier_bankruptcy')
        duration = int(params.get('duration_weeks', 4))
        affected = int(params.get('affected_suppliers', 1))
        has_backup = params.get('backup_available', 'yes') == 'yes'
        cs = currency_symbol
        fmt = SimulationService._fmt_money
        signed = SimulationService._fmt_signed

        impact_rates = {
            'supplier_bankruptcy': 0.3,
            'natural_disaster': 0.25,
            'logistics_failure': 0.15,
            'quality_recall': 0.2,
            'trade_war': 0.35
        }
        base_impact = impact_rates.get(disruption_type, 0.2)

        duration_mult = 1 + (duration - 1) * 0.15
        backup_factor = 0.4 if has_backup else 1.0

        total_impact = base_impact * duration_mult * backup_factor * affected
        revenue_loss = baseline['revenue'] * total_impact

        # When revenue is lost due to supply disruption, variable costs are also saved
        # (you don't incur COGS, shipping, etc. for units you can't sell)
        cost_ratio = baseline['costs'] / baseline['revenue'] if baseline['revenue'] > 0 else 0.7
        cost_ratio = min(max(cost_ratio, 0.5), 0.95)

        # Assume ~60% of costs are variable and saveable when production stops
        variable_cost_ratio = cost_ratio * 0.6
        cost_savings = revenue_loss * variable_cost_ratio

        mitigation_cost = 0 if has_backup else baseline['revenue'] * 0.05
        alt_cost = 0 if has_backup else baseline['costs'] * 0.1 * duration / 4

        # Costs go down by savings, up by mitigation/alternative sourcing
        cost_after = baseline['costs'] - cost_savings + mitigation_cost + alt_cost
        revenue_after = baseline['revenue'] - revenue_loss
        profit_after = revenue_after - cost_after
        profit_before = baseline['profit']
        net_profit = profit_after - profit_before

        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(revenue_after, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(cost_after, 2),
            'profit_before': round(profit_before, 2),
            'profit_after': round(profit_after, 2),
            'risk_score': 35 if has_backup else 70,
            'revenue_loss': round(revenue_loss, 2),
            'cost_savings': round(cost_savings, 2),
            'mitigation_cost': round(mitigation_cost + alt_cost, 2),
            'duration_weeks': duration,
            'recommendations': f"{disruption_type.replace('_', ' ').title()} for {duration} weeks. Revenue loss: {fmt(revenue_loss, cs)}. Cost savings: {fmt(cost_savings, cs)}. Backup available: {has_backup}. Mitigation cost: {fmt(mitigation_cost + alt_cost, cs)}. Net profit impact: {signed(net_profit, cs)}. " + ("Diversify suppliers." if not has_backup else "Monitor backup supplier capacity.")
        }

    # ============ DEFAULT FALLBACK ============
    @staticmethod
    def _calc_default(company_id, params, currency_symbol='$'):
        baseline = SimulationService._get_company_baseline(company_id)
        return {
            'revenue_before': round(baseline['revenue'], 2),
            'revenue_after': round(baseline['revenue'] * 1.05, 2),
            'cost_before': round(baseline['costs'], 2),
            'cost_after': round(baseline['costs'] * 1.03, 2),
            'profit_before': round(baseline['profit'], 2),
            'profit_after': round(baseline['revenue'] * 1.05 - baseline['costs'] * 1.03, 2),
            'risk_score': 40,
            'recommendations': 'Generic simulation - customize parameters for more accurate results.'
        }