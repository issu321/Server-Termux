import os
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__, 
                template_folder='templates',
                static_folder='static')
    
    app.config.from_object('config.settings.Config')
    
    # Initialize extensions
    from database.db import db, init_db
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
    
    # Login manager
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'info'
    
    @login_manager.user_loader
    def load_user(user_id):
        from database.models.user import User
        return User.query.get(int(user_id))
    
    # ==================== GLOBAL CURRENCY FILTER & CONTEXT ====================
    from config.constants import CURRENCY_SYMBOLS
    
    @app.template_filter('format_currency')
    def format_currency_filter(value, currency_code=None):
        """Format a number with the company's selected currency symbol.
        Usage: {{ value | format_currency }}  → auto-detects from session
        Usage: {{ value | format_currency('EUR') }}  → force EUR
        """
        if value is None:
            return '-'
        try:
            value = float(value)
        except (TypeError, ValueError):
            return str(value)
        
        # Auto-detect currency from session if not provided
        if currency_code is None:
            currency_code = session.get('company_currency', 'USD')
        
        symbol = CURRENCY_SYMBOLS.get(currency_code, '$')
        
        # Format: always show full number with commas, no decimals for large values
        if abs(value) >= 1000000000000:
            return f'{symbol}{value/1000000000000:.1f}T'
        elif abs(value) >= 1000000000:
            return f'{symbol}{value/1000000000:.1f}B'
        elif abs(value) >= 1000000:
            return f'{symbol}{value/1000000:.1f}M'
        elif abs(value) >= 1000:
            return f'{symbol}{value:,.0f}'
        else:
            return f'{symbol}{value:,.2f}'
    
    @app.context_processor
    def inject_currency():
        """Inject company currency and symbol into every template automatically."""
        from database.models.company import Company
        
        company_id = session.get('company_id')
        currency = session.get('company_currency', 'USD')
        
        # Always refresh from DB to catch updates
        if company_id:
            try:
                company = Company.query.get(company_id)
                if company and company.currency:
                    currency = company.currency
                    session['company_currency'] = currency
            except Exception:
                pass
        
        symbol = CURRENCY_SYMBOLS.get(currency, '$')
        
        return {
            'company_currency': currency,
            'currency_symbol': symbol,
            'currency_name': currency
        }
    # =======================================================================
    
    # Register blueprints
    from routes.auth import auth_bp
    from routes.dashboard import dashboard_bp
    from routes.business_twin import business_twin_bp
    from routes.simulation import simulation_bp
    from routes.forecasting import forecasting_bp
    from routes.risk_engine import risk_engine_bp
    from routes.analytics import analytics_bp
    from routes.reports import reports_bp
    from routes.documents import documents_bp
    from routes.settings import settings_bp
    # from routes.developer import developer_bp  # REMOVED - no developer page
    from routes.scenario_builder import scenario_bp
    from routes.market_intelligence import market_bp
    from routes.financial_modeling import financial_bp
    from routes.customer_simulator import customer_bp
    from routes.employee_simulator import employee_bp
    from routes.supply_chain_simulator import supply_chain_bp
    from routes.operations_simulator import operations_bp
    from routes.ai_insights import ai_insights_bp
    from routes.data_lake import data_lake_bp
    from routes.competition import competition_bp
    from routes.uploads import uploads_bp
    from routes.custom_twin import custom_twin_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(business_twin_bp, url_prefix='/business-twin')
    app.register_blueprint(simulation_bp, url_prefix='/simulation')
    app.register_blueprint(forecasting_bp, url_prefix='/forecasting')
    app.register_blueprint(risk_engine_bp, url_prefix='/risk')
    app.register_blueprint(analytics_bp, url_prefix='/analytics')
    app.register_blueprint(reports_bp, url_prefix='/reports')
    app.register_blueprint(documents_bp, url_prefix='/documents')
    app.register_blueprint(settings_bp, url_prefix='/settings')
    # app.register_blueprint(developer_bp, url_prefix='/developer')  # REMOVED
    app.register_blueprint(scenario_bp, url_prefix='/scenario')
    app.register_blueprint(market_bp, url_prefix='/market')
    app.register_blueprint(financial_bp, url_prefix='/financial')
    app.register_blueprint(customer_bp, url_prefix='/customer')
    app.register_blueprint(employee_bp, url_prefix='/employee')
    app.register_blueprint(supply_chain_bp, url_prefix='/supply-chain')
    app.register_blueprint(operations_bp, url_prefix='/operations')
    app.register_blueprint(ai_insights_bp, url_prefix='/ai-insights')
    app.register_blueprint(data_lake_bp, url_prefix='/data-lake')
    app.register_blueprint(competition_bp, url_prefix='/competition')
    app.register_blueprint(uploads_bp, url_prefix='/uploads')
    app.register_blueprint(custom_twin_bp, url_prefix='/business-twin')
    
    # Context processors
    @app.context_processor
    def inject_globals():
        from config.themes import THEMES
        theme_id = session.get('theme', app.config.get('DEFAULT_THEME', 'aurora_enterprise'))
        theme = THEMES.get(theme_id, THEMES['aurora_enterprise'])
        return {
            'app_version': app.config.get('APP_VERSION', '1.0.0'),
            'current_year': datetime.now().year,
            'theme': theme,
            'theme_id': theme_id,
            'all_themes': THEMES
        }
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return render_template('base.html', error='Page not found'), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('base.html', error='Internal server error'), 500
    
    # Health check
    @app.route('/health')
    def health():
        return jsonify({'status': 'healthy', 'timestamp': datetime.utcnow().isoformat()})
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)