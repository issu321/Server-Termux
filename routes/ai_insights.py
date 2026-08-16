from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from services.analytics_service import AnalyticsService
from services.risk_service import RiskService
from database.models.company import Company
from config.constants import CURRENCY_SYMBOLS

ai_insights_bp = Blueprint('ai_insights', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or database."""
    currency_code = session.get('company_currency')
    if not currency_code:
        company = Company.query.get(session.get('company_id'))
        currency_code = getattr(company, 'currency', None) if company else None
        if not currency_code:
            currency_code = 'USD'
    return CURRENCY_SYMBOLS.get(currency_code, '$')

@ai_insights_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    currency_symbol = _get_currency_symbol()
    summary = AnalyticsService.get_executive_summary(company_id)
    risk_summary = RiskService.get_risk_summary(company_id)
    trend = AnalyticsService.get_trend_data(company_id, 90)
    
    # Generate AI insights
    insights = []
    
    if summary['margin'] < 10:
        insights.append({
            'type': 'warning',
            'title': 'Low Profit Margin',
            'description': f'Your profit margin of {summary["margin"]:.1f}% is below the healthy threshold of 10%. Consider cost optimization or pricing review.',
            'confidence': 92,
            'action': 'Review pricing strategy and operating costs'
        })
    
    if summary['churn_rate'] > 10:
        insights.append({
            'type': 'warning',
            'title': 'High Customer Churn',
            'description': f'Churn rate of {summary["churn_rate"]:.1f}% is concerning. Industry average is 5-8%.',
            'confidence': 88,
            'action': 'Implement customer retention program'
        })
    
    if summary['low_stock'] > 0:
        insights.append({
            'type': 'alert',
            'title': 'Inventory Alert',
            'description': f'{summary["low_stock"]} items are below reorder point. Restock to avoid stockouts.',
            'confidence': 95,
            'action': 'Review inventory and place orders'
        })
    
    if summary['health_score'] > 80:
        insights.append({
            'type': 'success',
            'title': 'Strong Business Health',
            'description': f'Health score of {summary["health_score"]:.0f}/100 indicates strong business performance.',
            'confidence': 90,
            'action': 'Maintain current strategies'
        })
    
    insights.append({
        'type': 'info',
        'title': 'Growth Opportunity',
        'description': 'Based on current trends, consider expanding into adjacent markets or launching complementary products.',
        'confidence': 75,
        'action': 'Explore market expansion options'
    })
    
    return render_template('ai/ai_insights.html', 
                         insights=insights, 
                         summary=summary, 
                         risk_summary=risk_summary,
                         currency_symbol=currency_symbol)