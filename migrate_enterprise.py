#!/usr/bin/env python3
"""
Enterprise Migration Script - Add enterprise-grade features to the database

This script adds advanced financial metrics, growth tracking, AI predictions,
and performance optimizations to support large-scale enterprises.
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from database.db import db
from sqlalchemy import text

def migrate_enterprise_features():
    """Add enterprise-grade columns to the database."""
    print("=" * 70)
    print("  ENTERPRISE MIGRATION")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        # Add enterprise financial metrics
        print("\nAdding enterprise financial metrics...")
        
        # Financial ratios
        add_column('companies', 'gross_profit_margin', 'FLOAT', '0.0')
        add_column('companies', 'operating_margin', 'FLOAT', '0.0')
        add_column('companies', 'net_profit_margin', 'FLOAT', '0.0')
        add_column('companies', 'ebitda', 'FLOAT', '0.0')
        add_column('companies', 'ebitda_margin', 'FLOAT', '0.0')
        add_column('companies', 'return_on_equity', 'FLOAT', '0.0')
        add_column('companies', 'return_on_assets', 'FLOAT', '0.0')
        add_column('companies', 'current_ratio', 'FLOAT', '0.0')
        add_column('companies', 'quick_ratio', 'FLOAT', '0.0')
        add_column('companies', 'debt_to_equity', 'FLOAT', '0.0')
        
        # Enterprise valuation
        add_column('companies', 'market_cap', 'FLOAT', '0.0')
        add_column('companies', 'enterprise_value', 'FLOAT', '0.0')
        add_column('companies', 'book_value', 'FLOAT', '0.0')
        
        # Growth metrics
        add_column('companies', 'revenue_growth_rate', 'FLOAT', '0.0')
        add_column('companies', 'employee_growth_rate', 'FLOAT', '0.0')
        add_column('companies', 'customer_growth_rate', 'FLOAT', '0.0')
        
        # AI/ML Predictions
        add_column('companies', 'predicted_revenue_30d', 'FLOAT', '0.0')
        add_column('companies', 'predicted_revenue_90d', 'FLOAT', '0.0')
        add_column('companies', 'risk_score', 'FLOAT', '0.0')
        add_column('companies', 'opportunity_score', 'FLOAT', '0.0')
        
        # Performance tracking
        add_column('companies', 'last_analytics_update', 'DATETIME', 'NULL')
        add_column('companies', 'last_forecast_update', 'DATETIME', 'NULL')
        
        # Enterprise features
        add_column('companies', 'is_publicly_traded', 'BOOLEAN', '0')
        add_column('companies', 'stock_symbol', 'VARCHAR(20)', "''")
        add_column('companies', 'fiscal_year_end', 'VARCHAR(10)', "'12-31'")
        
        # Add indexes for performance
        print("\nAdding database indexes for enterprise performance...")
        add_index('companies', 'idx_company_industry_size', ['industry', 'company_size'])
        add_index('companies', 'idx_company_revenue', ['annual_revenue'])
        add_index('companies', 'idx_company_health', ['health_score'])
        add_index('companies', 'idx_company_active', ['is_active'])
        add_index('companies', 'idx_company_employees', ['employee_count'])
        
        # Update existing indexes
        add_index('companies', 'idx_company_name', ['company_name'])
        add_index('companies', 'idx_company_industry', ['industry'])
        add_index('companies', 'idx_company_country', ['country'])
        
        print("\n" + "=" * 70)
        print("  MIGRATION COMPLETE!")
        print("=" * 70)
        print("\nYour database now supports enterprise-grade features:")
        print("[OK] Advanced financial ratios (ROE, ROA, EBITDA, margins)")
        print("[OK] Enterprise valuation metrics (Market Cap, EV, Book Value)")
        print("[OK] Growth rate tracking (revenue, employee, customer)")
        print("[OK] AI/ML prediction fields (30d/90d forecasts, risk/opportunity scores)")
        print("[OK] Performance optimization indexes")
        print("[OK] Public company support (stock symbols, fiscal years)")
        print("\nNext: Run the financial calculation service to populate metrics")
        print("=" * 70)

def add_column(table, column, data_type, default_value):
    """Add a column to a table if it doesn't exist."""
    try:
        # Check if column exists using SQLite PRAGMA
        result = db.session.execute(text(f"""
            PRAGMA table_info({table})
        """)).fetchall()
        
        column_exists = any(row[1] == column for row in result)
        
        if not column_exists:
            # Add column
            db.session.execute(text(f"""
                ALTER TABLE {table} 
                ADD COLUMN {column} {data_type} DEFAULT {default_value}
            """))
            db.session.commit()
            print(f"  [OK] Added {table}.{column}")
        else:
            print(f"  [-] {table}.{column} already exists")
    except Exception as e:
        print(f"  [ERROR] Error adding {table}.{column}: {e}")
        db.session.rollback()

def add_index(table, index_name, columns):
    """Add an index to a table if it doesn't exist."""
    try:
        # Check if index exists
        result = db.session.execute(text(f"""
            SELECT COUNT(*) as count 
            FROM sqlite_master 
            WHERE type = 'index' AND name = '{index_name}'
        """)).fetchone()
        
        if result[0] == 0:
            # Create index
            columns_str = ', '.join(columns)
            db.session.execute(text(f"""
                CREATE INDEX {index_name} ON {table} ({columns_str})
            """))
            db.session.commit()
            print(f"  [OK] Created index {index_name}")
        else:
            print(f"  [-] Index {index_name} already exists")
    except Exception as e:
        print(f"  [ERROR] Error creating index {index_name}: {e}")
        db.session.rollback()

if __name__ == "__main__":
    migrate_enterprise_features()
