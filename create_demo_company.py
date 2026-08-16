#!/usr/bin/env python3
"""
Create Demo Company - Showcase Enterprise Features

This script creates a demo company (similar to Google/Microsoft/Nvidia scale)
to demonstrate the enterprise-grade financial calculations and AI predictions.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from database.db import db
from database.models.company import Company
from database.models.financial import FinancialRecord
from datetime import datetime, timedelta
import random

def create_demo_company():
    """Create a demo company similar to Google/Microsoft/Nvidia scale."""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 70)
        print("  CREATING DEMO COMPANY (Tech Giant Scale)")
        print("=" * 70)
        
        # Create a company similar to Google/Microsoft/Nvidia
        demo_company = Company(
            company_name="TechCorp Global Enterprises",
            business_name="TechCorp Global",
            owner_name="Dr. Sarah Chen",
            ceo_name="Alex Rodriguez",
            industry="Technology",
            business_type="Corporation",
            description="A global technology company specializing in AI, cloud computing, and enterprise software solutions.",
            company_size="1000+",
            employee_count=8500,  # Large enterprise
            customer_count=2500000,  # Millions of customers
            annual_revenue=45000000000,  # $45B annual revenue (Google scale)
            total_equity=150000000000,  # $150B equity
            total_debt=25000000000,  # $25B debt
            currency="USD",
            country="United States",
            city="Mountain View",
            timezone="America/Los_Angeles",
            tax_type="Corporate Tax",
            tax_rate=21.0,
            website="https://techcorp.global",
            email="contact@techcorp.global",
            founded_date=datetime(1998, 9, 4),  # Same as Google
            registration_number="CA-123456789",
            is_publicly_traded=True,
            stock_symbol="TCGE",
            fiscal_year_end="12-31",
            health_score=92.5
        )
        
        db.session.add(demo_company)
        db.session.commit()
        
        print(f"[OK] Created {demo_company.company_name}")
        print(f"  - Employees: {demo_company.employee_count:,}")
        print(f"  - Annual Revenue: ${demo_company.annual_revenue:,.0f}")
        print(f"  - Market Cap: ${demo_company.market_cap:,.0f}")
        
        # Create realistic financial transactions for the last 12 months
        print("\n[OK] Creating financial transactions...")
        
        base_revenue = demo_company.annual_revenue / 12
        base_expenses = base_revenue * 0.75  # 75% expense ratio
        
        for i in range(12):  # Last 12 months
            transaction_date = datetime.utcnow() - timedelta(days=30*i)
            
            # Add some realistic variation (±10%)
            revenue_variation = random.uniform(0.9, 1.1)
            expense_variation = random.uniform(0.9, 1.1)
            
            # Revenue transaction
            revenue = FinancialRecord(
                company_id=demo_company.id,
                transaction_type='revenue',
                amount=base_revenue * revenue_variation,
                description=f"Monthly revenue - {transaction_date.strftime('%B %Y')}",
                transaction_date=transaction_date.date(),
                category='operating_revenue'
            )
            db.session.add(revenue)
            
            # Expense transaction
            expense = FinancialRecord(
                company_id=demo_company.id,
                transaction_type='expense',
                amount=base_expenses * expense_variation,
                description=f"Monthly expenses - {transaction_date.strftime('%B %Y')}",
                transaction_date=transaction_date.date(),
                category='operating_expenses'
            )
            db.session.add(expense)
        
        db.session.commit()
        print(f"[OK] Created 24 financial transactions (12 months)")
        
        # Now calculate enterprise metrics
        print("\n[OK] Calculating enterprise financial metrics...")
        from services.enterprise_service import EnterpriseService
        
        EnterpriseService.calculate_all_metrics(demo_company.id)
        
        # Refresh the company data to show calculated metrics
        db.session.refresh(demo_company)
        
        print("\n" + "=" * 70)
        print("  ENTERPRISE METRICS CALCULATED")
        print("=" * 70)
        print(f"\nFinancial Ratios:")
        print(f"  - Gross Profit Margin: {demo_company.gross_profit_margin:.2f}%")
        print(f"  - EBITDA Margin: {demo_company.ebitda_margin:.2f}%")
        print(f"  - Return on Equity: {demo_company.return_on_equity:.2f}%")
        print(f"  - Return on Assets: {demo_company.return_on_assets:.2f}%")
        print(f"  - Current Ratio: {demo_company.current_ratio:.2f}")
        print(f"  - Debt-to-Equity: {demo_company.debt_to_equity:.2f}")
        
        print(f"\nValuation Metrics:")
        print(f"  - Market Cap: ${demo_company.market_cap:,.0f}")
        print(f"  - Enterprise Value: ${demo_company.enterprise_value:,.0f}")
        print(f"  - Book Value: ${demo_company.book_value:.2f}")
        
        print(f"\nGrowth Rates:")
        print(f"  - Revenue Growth: {demo_company.revenue_growth_rate:.2f}%")
        print(f"  - Employee Growth: {demo_company.employee_growth_rate:.2f}%")
        print(f"  - Customer Growth: {demo_company.customer_growth_rate:.2f}%")
        
        print(f"\nAI/ML Predictions:")
        print(f"  - 30-Day Revenue Forecast: ${demo_company.predicted_revenue_30d:,.0f}")
        print(f"  - 90-Day Revenue Forecast: ${demo_company.predicted_revenue_90d:,.0f}")
        print(f"  - Risk Score: {demo_company.risk_score:.1f}/100")
        print(f"  - Opportunity Score: {demo_company.opportunity_score:.1f}/100")
        
        print("\n" + "=" * 70)
        print("  DEMO COMPANY CREATED SUCCESSFULLY!")
        print("=" * 70)
        print("\nThis company demonstrates enterprise-grade features:")
        print("[OK] Real financial ratios calculated from transaction data")
        print("[OK] Enterprise valuation metrics (Market Cap, EV, Book Value)")
        print("[OK] Growth rate tracking based on historical data")
        print("[OK] AI/ML predictions using machine learning models")
        print("[OK] Risk and opportunity scoring")
        print("[OK] Support for publicly traded companies")
        print("\nScale: Similar to Google/Microsoft/Nvidia")
        print("- 8,500 employees")
        print("- $45B annual revenue")
        print("- 2.5M customers")
        print("- Publicly traded with stock symbol")
        print("=" * 70)

if __name__ == "__main__":
    create_demo_company()
