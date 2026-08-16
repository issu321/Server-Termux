#!/usr/bin/env python3
"""
init_db.py — Create all database tables from scratch.

Run this script to initialize the database:
    python init_db.py
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from database.db import db

# Import all models to ensure they are registered
from database.models import *

def init_database():
    print("=" * 70)
    print("  DATABASE INITIALIZATION")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        print("\nCreating all tables...")
        db.create_all()
        print("[OK] All tables created successfully!")
        
        # List created tables
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"\nTables created ({len(tables)} total):")
        for table in sorted(tables):
            print(f"  • {table}")
        
        print("\n" + "=" * 70)
        print("  DATABASE READY!")
        print("=" * 70)
        print("\nYou can now start the application and register users.")
        print("Run: python app.py")
        print("=" * 70)

if __name__ == "__main__":
    init_database()
