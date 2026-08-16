from database.db import db
from database.models.risk import Risk, RiskFactor
from database.models.company import Company
from config.constants import RISK_CATEGORIES
import numpy as np

class RiskService:
    @staticmethod
    def assess_all_risks(company_id):
        risks = Risk.query.filter_by(company_id=company_id).all()
        if not risks:
            RiskService._generate_default_risks(company_id)
            risks = Risk.query.filter_by(company_id=company_id).all()
        
        for risk in risks:
            risk.calculate_score()
        db.session.commit()
        
        return risks
    
    @staticmethod
    def _generate_default_risks(company_id):
        from database.models.financial import FinancialRecord
        from database.models.employee import Employee
        from database.models.customer import Customer
        from database.models.inventory import Inventory
        from database.models.supplier import Supplier
        from sqlalchemy import func
        
        company = Company.query.get(company_id)
        if not company:
            return
        
        # --- Pull real financials ---
        total_revenue = db.session.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.company_id == company_id,
            FinancialRecord.transaction_type == 'revenue'
        ).scalar() or company.annual_revenue or 1000000
        
        total_expense = db.session.query(func.sum(FinancialRecord.amount)).filter(
            FinancialRecord.company_id == company_id,
            FinancialRecord.transaction_type == 'expense'
        ).scalar() or (company.annual_revenue * 0.8 if company.annual_revenue else 800000)
        
        profit = float(total_revenue) - float(total_expense)
        margin = profit / float(total_revenue) if total_revenue else 0.1
        
        # --- Pull operational counts ---
        employee_count = db.session.query(func.count(Employee.id)).filter(
            Employee.company_id == company_id,
            Employee.status == 'active'
        ).scalar() or 50
        
        customer_count = db.session.query(func.count(Customer.id)).filter(
            Customer.company_id == company_id,
            Customer.status == 'active'
        ).scalar() or 100
        
        supplier_count = db.session.query(func.count(Supplier.id)).filter(
            Supplier.company_id == company_id
        ).scalar() or 5
        
        inventory_items = Inventory.query.filter_by(company_id=company_id, is_active=True).count()
        total_inventory_value = db.session.query(func.sum(Inventory.quantity_on_hand * Inventory.unit_cost)).filter(
            Inventory.company_id == company_id,
            Inventory.is_active == True
        ).scalar() or 0
        
        # --- Derive realistic risk probabilities & impacts ---
        # Financial: worse margin = higher risk
        liquidity_prob = 0.25 if profit > 0 else 0.75
        liquidity_impact = 0.5 if margin > 0.15 else 0.85 if margin > 0 else 0.95
        
        credit_prob = min(0.2 + (1000 / max(customer_count, 1)) * 0.01, 0.6)
        credit_impact = 0.45
        
        # Operational: small team = higher single-point-of-failure risk
        process_prob = min(0.2 + (50 / max(employee_count, 1)) * 0.1, 0.5)
        process_impact = 0.5 if employee_count > 20 else 0.65
        
        system_prob = 0.25
        system_impact = 0.45
        
        # Market: low customers = volatile demand
        demand_prob = min(0.3 + (500 / max(customer_count, 1)) * 0.05, 0.7)
        demand_impact = 0.55
        
        comp_prob = min(0.35 + (1000 / max(total_revenue, 1)) * 0.05, 0.7)
        comp_impact = 0.55
        
        # Supply chain: few suppliers = high dependency
        supplier_prob = min(0.3 + (10 / max(supplier_count, 1)) * 0.05, 0.7)
        supplier_impact = 0.6 if supplier_count < 3 else 0.45
        
        logistics_prob = 0.3
        logistics_impact = 0.45
        
        # Inventory: high value relative to revenue = overstock risk
        inventory_ratio = float(total_inventory_value) / max(float(total_revenue), 1)
        overstock_prob = min(0.25 + inventory_ratio * 2, 0.7)
        overstock_impact = 0.4
        
        stockout_prob = min(0.3 + (1 / max(inventory_items, 1)) * 0.1, 0.6)
        stockout_impact = 0.55
        
        # Growth: low margin constrains growth
        growth_prob = 0.3 if margin > 0.15 else 0.5
        growth_impact = 0.5
        
        talent_prob = min(0.3 + (100 / max(employee_count, 1)) * 0.05, 0.6)
        talent_impact = 0.55
        
        # Competition
        price_prob = 0.35
        price_impact = 0.5
        
        innov_prob = 0.4
        innov_impact = 0.55
        
        # Economic
        recession_prob = 0.3
        recession_impact = 0.75 if margin < 0.1 else 0.6
        
        inflation_prob = 0.45
        inflation_impact = 0.5 if margin > 0.2 else 0.65
        
        # Cash flow
        wc_prob = 0.35 if profit > 0 else 0.7
        wc_impact = 0.55
        
        bad_debt_prob = 0.3
        bad_debt_impact = 0.45
        
        risk_configs = [
            ('financial', 'Liquidity Risk', 
             'Ability to meet short-term obligations. Tight margins or negative cash flow increase this risk significantly.', 
             liquidity_prob, liquidity_impact),
            ('financial', 'Credit Risk', 
             'Exposure to customer payment defaults. Higher with fewer customers or weak credit controls.', 
             credit_prob, credit_impact),
            ('operational', 'Process Failure Risk', 
             'Breakdown of core business processes. Smaller teams have higher single-point-of-failure exposure.', 
             process_prob, process_impact),
            ('operational', 'System Downtime Risk', 
             'IT infrastructure failure disrupting operations. Critical for digital-dependent businesses.', 
             system_prob, system_impact),
            ('market', 'Demand Fluctuation', 
             'Revenue volatility due to changing customer demand. Higher with concentrated customer base.', 
             demand_prob, demand_impact),
            ('market', 'Competition Risk', 
             'Market share erosion from aggressive competitors. Intensifies in low-margin environments.', 
             comp_prob, comp_impact),
            ('supply_chain', 'Supplier Failure', 
             'Dependency on limited suppliers causing production stoppages. Critical with <3 active suppliers.', 
             supplier_prob, supplier_impact),
            ('supply_chain', 'Logistics Disruption', 
             'Transportation delays or freight cost spikes affecting delivery timelines.', 
             logistics_prob, logistics_impact),
            ('inventory', 'Overstock Risk', 
             'Excess inventory tying up working capital and increasing carrying costs.', 
             overstock_prob, overstock_impact),
            ('inventory', 'Stockout Risk', 
             'Inventory shortages leading to lost sales and customer dissatisfaction.', 
             stockout_prob, stockout_impact),
            ('growth', 'Overexpansion Risk', 
             'Growing operations faster than cash flow or management capacity can support.', 
             growth_prob, growth_impact),
            ('growth', 'Talent Shortage', 
             'Inability to hire or retain skilled employees needed for scaling.', 
             talent_prob, talent_impact),
            ('competition', 'Price War Risk', 
             'Competitors forcing down prices, compressing already thin margins.', 
             price_prob, price_impact),
            ('competition', 'Innovation Gap', 
             'Falling behind competitor product development or technology adoption.', 
             innov_prob, innov_impact),
            ('economic', 'Recession Impact', 
             'Macroeconomic downturn reducing customer spending and contract values.', 
             recession_prob, recession_impact),
            ('economic', 'Inflation Risk', 
             'Rising input costs that cannot be fully passed to customers, squeezing margins.', 
             inflation_prob, inflation_impact),
            ('cashflow', 'Working Capital Crunch', 
             'Insufficient liquid assets to cover payroll, suppliers, and operating expenses.', 
             wc_prob, wc_impact),
            ('cashflow', 'Bad Debt Risk', 
             'Uncollectible accounts receivables writing off expected revenue.', 
             bad_debt_prob, bad_debt_impact),
        ]
        
        for category, name, desc, prob, impact in risk_configs:
            risk = Risk(
                company_id=company_id,
                name=name,
                category=category,
                description=desc,
                probability=round(prob, 2),
                impact=round(impact, 2)
            )
            risk.calculate_score()
            db.session.add(risk)
        
        db.session.commit()
    
    @staticmethod
    def get_risk_summary(company_id):
        risks = Risk.query.filter_by(company_id=company_id).all()
        if not risks:
            risks = RiskService.assess_all_risks(company_id)
        
        category_scores = {}
        category_explanations = {
            'financial': 'Profitability, liquidity, and credit exposure.',
            'operational': 'Internal processes, systems, and workforce stability.',
            'market': 'Customer demand volatility and competitive positioning.',
            'supply_chain': 'Supplier reliability and logistics resilience.',
            'inventory': 'Stock levels, turnover, and carrying cost efficiency.',
            'growth': 'Scaling capacity and talent pipeline sufficiency.',
            'competition': 'Price pressure and innovation velocity vs. rivals.',
            'economic': 'Macroeconomic sensitivity and inflation exposure.',
            'cashflow': 'Short-term liquidity and receivables quality.'
        }
        
        for cat in RISK_CATEGORIES:
            cat_risks = [r for r in risks if r.category == cat]
            if cat_risks:
                avg_score = sum(r.risk_score for r in cat_risks) / len(cat_risks)
                max_score = max(r.risk_score for r in cat_risks)
                critical = len([r for r in cat_risks if r.risk_level == 'critical'])
                high = len([r for r in cat_risks if r.risk_level == 'high'])
                
                # Generate category-specific advice
                if avg_score >= 70:
                    advice = f"Critical exposure in {cat.replace('_', ' ')}. Immediate mitigation required."
                elif avg_score >= 40:
                    advice = f"Elevated {cat.replace('_', ' ')} risk. Monitor closely and prepare contingency plans."
                elif avg_score >= 20:
                    advice = f"Moderate {cat.replace('_', ' ')} risk. Maintain current controls."
                else:
                    advice = f"Low {cat.replace('_', ' ')} risk. Continue standard monitoring."
                
                category_scores[cat] = {
                    'avg_score': round(avg_score, 1),
                    'max_score': round(max_score, 1),
                    'risk_count': len(cat_risks),
                    'critical_count': critical,
                    'high_count': high,
                    'explanation': category_explanations.get(cat, ''),
                    'advice': advice,
                    'risks': [r.to_dict() for r in cat_risks]
                }
        
        overall = sum(r.risk_score for r in risks) / len(risks) if risks else 50
        
        # Top 3 risks by score
        top_risks = sorted([r.to_dict() for r in risks], key=lambda x: x['risk_score'], reverse=True)[:3]
        
        # Overall recommendation
        if overall >= 70:
            overall_advice = "CRITICAL: Your aggregate risk profile is severe. Immediate executive intervention and emergency planning are required."
        elif overall >= 40:
            overall_advice = "HIGH: Significant risk exposure detected. Prioritize mitigation for top-scoring categories and review insurance coverage."
        elif overall >= 20:
            overall_advice = "MODERATE: Balanced risk profile with some areas needing attention. Quarterly review recommended."
        else:
            overall_advice = "LOW: Risk environment is well-controlled. Focus on prevention and continuous improvement."
        
        return {
            'overall_score': round(overall, 1),
            'risk_level': 'critical' if overall >= 70 else 'high' if overall >= 40 else 'medium' if overall >= 20 else 'low',
            'total_risks': len(risks),
            'critical_count': len([r for r in risks if r.risk_level == 'critical']),
            'high_count': len([r for r in risks if r.risk_level == 'high']),
            'medium_count': len([r for r in risks if r.risk_level == 'medium']),
            'low_count': len([r for r in risks if r.risk_level == 'low']),
            'category_scores': category_scores,
            'top_risks': top_risks,
            'overall_advice': overall_advice
        }