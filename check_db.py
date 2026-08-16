#!/usr/bin/env python3
"""
Check Database Schema - Verify columns exist
"""

import sqlite3
import os

def check_database():
    db_path = "c:\\Users\\USSUROYAL\\Documents\\Programming\\instance\\business_simulator.db"
    
    if not os.path.exists(db_path):
        print(f"❌ Database file not found: {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get table info
    cursor.execute("PRAGMA table_info(companies)")
    columns = cursor.fetchall()
    
    print("=" * 70)
    print("DATABASE SCHEMA CHECK")
    print("=" * 70)
    print(f"Database: {db_path}")
    print(f"Total columns: {len(columns)}")
    print()
    
    # Check for specific columns
    column_names = [col[1] for col in columns]
    
    required_columns = [
        'altman_z_score',
        'piotroski_f_score', 
        'beneish_m_score',
        'economic_value_added',
        'free_cash_flow',
        'monte_carlo_valuation',
        'prediction_accuracy',
        'prediction_confidence'
    ]
    
    print("Checking required columns:")
    print("-" * 70)
    
    missing_columns = []
    for col in required_columns:
        if col in column_names:
            print(f"[OK] {col}")
        else:
            print(f"[MISSING] {col}")
            missing_columns.append(col)
    
    print()
    print("=" * 70)
    
    if missing_columns:
        print(f"[ERROR] {len(missing_columns)} columns are missing!")
        print("Missing columns:", missing_columns)
    else:
        print("[SUCCESS] All required columns exist!")
    
    print("=" * 70)

    
    # Show all columns
    print()
    print("All columns in 'companies' table:")
    print("-" * 70)
    for i, col in enumerate(columns, 1):
        col_name = col[1]
        col_type = col[2]
        print(f"{i:3d}. {col_name:<30} {col_type}")
    
    conn.close()

if __name__ == "__main__":
    check_database()