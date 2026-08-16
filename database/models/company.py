from database.db import db
from datetime import datetime
from sqlalchemy import Index

class Company(db.Model):
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(200), nullable=False, index=True)
    business_name = db.Column(db.String(200), nullable=False)
    owner_name = db.Column(db.String(200), nullable=False)
    ceo_name = db.Column(db.String(200), nullable=False)
    industry = db.Column(db.String(100), index=True)
    business_type = db.Column(db.String(50))
    description = db.Column(db.Text)
    company_size = db.Column(db.String(20), index=True)
    employee_count = db.Column(db.Integer, default=0, index=True)
    customer_count = db.Column(db.Integer, default=0)
    annual_revenue = db.Column(db.Float, default=0.0)
    total_equity = db.Column(db.Float, default=0.0)
    total_debt = db.Column(db.Float, default=0.0)
    currency = db.Column(db.String(10), default='USD')
    country = db.Column(db.String(100), index=True)
    city = db.Column(db.String(100))
    timezone = db.Column(db.String(100), default='UTC')
    tax_type = db.Column(db.String(50))
    tax_rate = db.Column(db.Float, default=0.0)
    logo_path = db.Column(db.String(255))
    website = db.Column(db.String(255))
    email = db.Column(db.String(120))
    mobile = db.Column(db.String(50))
    whatsapp = db.Column(db.String(50))
    telegram = db.Column(db.String(50))
    founded_date = db.Column(db.Date)
    registration_number = db.Column(db.String(100))
    health_score = db.Column(db.Float, default=75.0)
    is_active = db.Column(db.Boolean, default=True, index=True)
    is_publicly_traded = db.Column(db.Boolean, default=False)
    stock_symbol = db.Column(db.String(20))
    fiscal_year_end = db.Column(db.String(10), default='12-31')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Enterprise Financial Metrics
    gross_profit_margin = db.Column(db.Float, default=0.0)
    operating_margin = db.Column(db.Float, default=0.0)
    net_profit_margin = db.Column(db.Float, default=0.0)
    ebitda = db.Column(db.Float, default=0.0)
    ebitda_margin = db.Column(db.Float, default=0.0)
    return_on_equity = db.Column(db.Float, default=0.0)
    return_on_assets = db.Column(db.Float, default=0.0)
    current_ratio = db.Column(db.Float, default=0.0)
    quick_ratio = db.Column(db.Float, default=0.0)
    debt_to_equity = db.Column(db.Float, default=0.0)
    
    # Advanced Financial Metrics (Fortune 500 Grade)
    altman_z_score = db.Column(db.Float, default=0.0)  # Bankruptcy prediction
    piotroski_f_score = db.Column(db.Integer, default=0)  # Financial strength (0-9)
    beneish_m_score = db.Column(db.Float, default=0.0)  # Earnings manipulation detection
    economic_value_added = db.Column(db.Float, default=0.0)  # EVA
    free_cash_flow = db.Column(db.Float, default=0.0)  # FCF
    
    # Enterprise Valuation
    market_cap = db.Column(db.Float, default=0.0)
    enterprise_value = db.Column(db.Float, default=0.0)
    book_value = db.Column(db.Float, default=0.0)
    
    # Advanced Valuation Metrics
    monte_carlo_valuation = db.Column(db.JSON)  # Stores Monte Carlo results as JSON
    real_options_value = db.Column(db.Float, default=0.0)  # Real options valuation
    
    # Growth Metrics
    revenue_growth_rate = db.Column(db.Float, default=0.0)
    employee_growth_rate = db.Column(db.Float, default=0.0)
    customer_growth_rate = db.Column(db.Float, default=0.0)
    
    # AI/ML Predictions
    predicted_revenue_30d = db.Column(db.Float, default=0.0)
    predicted_revenue_90d = db.Column(db.Float, default=0.0)
    risk_score = db.Column(db.Float, default=0.0)
    opportunity_score = db.Column(db.Float, default=0.0)
    
    # AI/ML Model Performance
    prediction_accuracy = db.Column(db.Float, default=0.0)  # R-squared score
    prediction_confidence = db.Column(db.Float, default=0.0)  # Confidence interval
    
    # Performance Tracking
    last_analytics_update = db.Column(db.DateTime)
    last_forecast_update = db.Column(db.DateTime)
    
    # Automated Insights (stored as JSON)
    insights = db.Column(db.JSON)  # Array of automated insights
    recommendations = db.Column(db.JSON)  # Array of AI recommendations
    
    # Risk Assessment
    risk_factors = db.Column(db.JSON)  # Detailed risk factor analysis
    opportunity_factors = db.Column(db.JSON)  # Detailed opportunity analysis
    
    # Database Indexes for Performance
    __table_args__ = (
        Index('idx_company_industry_size', 'industry', 'company_size'),
        Index('idx_company_revenue', 'annual_revenue'),
        Index('idx_company_health', 'health_score'),
        Index('idx_company_active', 'is_active'),
    )

    def calculate_financial_ratios(self):
        """Calculate key financial ratios based on current data."""
        if self.annual_revenue > 0:
            # Calculate margins based on financial records
            from database.models.financial import FinancialRecord
            from sqlalchemy import func
            
            total_revenue = db.session.query(func.sum(FinancialRecord.amount)).filter(
                FinancialRecord.company_id == self.id,
                FinancialRecord.transaction_type == 'revenue'
            ).scalar() or self.annual_revenue
            
            total_expenses = db.session.query(func.sum(FinancialRecord.amount)).filter(
                FinancialRecord.company_id == self.id,
                FinancialRecord.transaction_type == 'expense'
            ).scalar() or (self.annual_revenue * 0.8)
            
            gross_profit = total_revenue - total_expenses
            
            self.gross_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            self.operating_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            self.net_profit_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            # EBITDA calculation (simplified)
            self.ebitda = gross_profit * 0.85  # Assume 15% operating expenses
            self.ebitda_margin = (self.ebitda / total_revenue * 100) if total_revenue > 0 else 0
            
            # Return ratios
            if self.total_equity > 0:
                self.return_on_equity = (gross_profit / self.total_equity * 100)
            
            total_assets = self.total_equity + self.total_debt
            if total_assets > 0:
                self.return_on_assets = (gross_profit / total_assets * 100)
            
            # Liquidity ratios
            current_assets = self.total_equity * 0.6  # Assume 60% of equity is current
            current_liabilities = self.total_debt * 0.3  # Assume 30% of debt is current
            
            self.current_ratio = (current_assets / current_liabilities) if current_liabilities > 0 else 0
            self.quick_ratio = (current_assets * 0.8 / current_liabilities) if current_liabilities > 0 else 0
            
            # Leverage ratios
            self.debt_to_equity = (self.total_debt / self.total_equity) if self.total_equity > 0 else 0
            
            # Enterprise value calculations
            self.enterprise_value = self.market_cap + self.total_debt - self.total_equity
            
            db.session.commit()

    def update_growth_rates(self):
        """Calculate growth rates based on historical data."""
        from database.models.analytics import Analytics
        from sqlalchemy import func
        
        # Get historical data
        historical_data = Analytics.query.filter(
            Analytics.company_id == self.id,
            Analytics.metric_type.in_(['revenue', 'employee_count', 'customer_count'])
        ).order_by(Analytics.created_at.desc()).limit(12).all()
        
        if len(historical_data) >= 2:
            # Calculate month-over-month growth rates
            latest = historical_data[0]
            previous = historical_data[-1]
            
            months_diff = (latest.created_at - previous.created_at).days / 30.44
            
            if months_diff > 0:
                if latest.metric_value > 0 and previous.metric_value > 0:
                    self.revenue_growth_rate = ((latest.metric_value / previous.metric_value) ** (1/months_diff) - 1) * 100
                
                # Employee and customer growth rates would be calculated similarly
                # For now, use simplified calculations
                self.employee_growth_rate = self.employee_growth_rate * 0.9  # Decay factor
                self.customer_growth_rate = self.customer_growth_rate * 0.9  # Decay factor

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'business_name': self.business_name,
            'owner_name': self.owner_name,
            'ceo_name': self.ceo_name,
            'industry': self.industry,
            'business_type': self.business_type,
            'company_size': self.company_size,
            'employee_count': self.employee_count,
            'customer_count': getattr(self, 'customer_count', 0),
            'annual_revenue': self.annual_revenue,
            'total_equity': getattr(self, 'total_equity', 0.0),
            'total_debt': getattr(self, 'total_debt', 0.0),
            'currency': self.currency,
            'country': self.country,
            'city': self.city,
            'timezone': self.timezone,
            'health_score': self.health_score,
            'logo_path': self.logo_path,
            'is_publicly_traded': self.is_publicly_traded,
            'stock_symbol': self.stock_symbol,
            'fiscal_year_end': self.fiscal_year_end,
            # Financial ratios
            'gross_profit_margin': self.gross_profit_margin,
            'operating_margin': self.operating_margin,
            'net_profit_margin': self.net_profit_margin,
            'ebitda': self.ebitda,
            'ebitda_margin': self.ebitda_margin,
            'return_on_equity': self.return_on_equity,
            'return_on_assets': self.return_on_assets,
            'current_ratio': self.current_ratio,
            'quick_ratio': self.quick_ratio,
            'debt_to_equity': self.debt_to_equity,
            # Advanced Financial Metrics (Fortune 500 Grade)
            'altman_z_score': getattr(self, 'altman_z_score', 0.0),
            'piotroski_f_score': getattr(self, 'piotroski_f_score', 0),
            'beneish_m_score': getattr(self, 'beneish_m_score', 0.0),
            'economic_value_added': getattr(self, 'economic_value_added', 0.0),
            'free_cash_flow': getattr(self, 'free_cash_flow', 0.0),
            # Valuation
            'market_cap': self.market_cap,
            'enterprise_value': self.enterprise_value,
            'book_value': self.book_value,
            # Advanced Valuation Metrics
            'monte_carlo_valuation': getattr(self, 'monte_carlo_valuation', None),
            'real_options_value': getattr(self, 'real_options_value', 0.0),
            # Growth rates
            'revenue_growth_rate': self.revenue_growth_rate,
            'employee_growth_rate': self.employee_growth_rate,
            'customer_growth_rate': self.customer_growth_rate,
            # AI Predictions
            'predicted_revenue_30d': self.predicted_revenue_30d,
            'predicted_revenue_90d': self.predicted_revenue_90d,
            'risk_score': self.risk_score,
            'opportunity_score': self.opportunity_score,
            # AI/ML Model Performance
            'prediction_accuracy': getattr(self, 'prediction_accuracy', 0.0),
            'prediction_confidence': getattr(self, 'prediction_confidence', 0.0),
            # Automated Insights
            'insights': getattr(self, 'insights', []),
            'recommendations': getattr(self, 'recommendations', []),
            'risk_factors': getattr(self, 'risk_factors', {}),
            'opportunity_factors': getattr(self, 'opportunity_factors', {}),
        }

    def __repr__(self):
        return f"<Company {self.company_name}>"

