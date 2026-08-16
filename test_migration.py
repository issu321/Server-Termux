#!/usr/bin/env python3
"""
Test Migration - Try to add a column and see the actual error
"""

import sys
import os

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from app import app
from database.db import db
from sqlalchemy import text
import traceback

def test_add_column():
    """Test adding a column and show the actual error."""
    
    print("="*70)
    print("TESTING MIGRATION - Adding altman_z_score column")
    print("="*70)
    
    with app.app_context():
        try:
            print("Attempting to add column...")
            db.session.execute(text("""
                ALTER TABLE companies ADD COLUMN altman_z_score FLOAT
            """))
            print("✓ ALTER TABLE executed successfully")
            
            db.session.commit()
            print("✓ Transaction committed successfully")
            
            # Verify
            result = db.session.execute(text("""
                PRAGMA table_info(companies)
            """)).fetchall()
            
            columns = [row[1] for row in result]
            if 'altman_z_score' in columns:
                print("✓ Column successfully added!")
            else:
                print("✗ Column was NOT added (this shouldn't happen)")
            
            return True
            
        except Exception as e:
            print(f"✗ ERROR occurred:")
            print(f"  Error type: {type(e).__name__}")
            print(f"  Error message: {str(e)}")
            print()
            print("Full traceback:")
            traceback.print_exc()
            db.session.rollback()
            return False

if __name__ == "__main__":
    success = test_add_column()
    if success:
        print("\n✓ Test PASSED")
    else:
        print("\n✗ Test FAILED")