#!/usr/bin/env python3
"""
Add missing columns to database with detailed error reporting
"""

import sqlite3
import traceback

def add_columns():
    db_path = "c:\\Users\\USSUROYAL\\Documents\\Programming\\instance\\business_simulator.db"
    
    print("="*70)
    print("ADDING MISSING COLUMNS TO DATABASE")
    print("="*70)
    print(f"Database: {db_path}")
    print()
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check current columns first
    cursor.execute("PRAGMA table_info(companies)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    print(f"Current columns: {len(existing_columns)}")
    print()
    
    columns_to_add = [
        ("altman_z_score", "FLOAT"),
        ("piotroski_f_score", "INTEGER"),
        ("beneish_m_score", "FLOAT"),
        ("economic_value_added", "FLOAT"),
        ("free_cash_flow", "FLOAT"),
        ("monte_carlo_valuation", "TEXT"),
        ("real_options_value", "FLOAT"),
        ("prediction_accuracy", "FLOAT"),
        ("prediction_confidence", "FLOAT"),
        ("insights", "TEXT"),
        ("recommendations", "TEXT"),
        ("risk_factors", "TEXT"),
        ("opportunity_factors", "TEXT")
    ]
    
    added = 0
    skipped = 0
    errors = 0
    
    for col_name, col_type in columns_to_add:
        if col_name in existing_columns:
            print(f"[-] {col_name} already exists, skipping")
            skipped += 1
            continue
            
        try:
            sql = f"ALTER TABLE companies ADD COLUMN {col_name} {col_type}"
            print(f"[+] Adding {col_name} ({col_type})...")
            cursor.execute(sql)
            print(f"    SUCCESS")
            added += 1
            
        except Exception as e:
            print(f"    ERROR: {e}")
            errors += 1
            traceback.print_exc()
    
    print()
    print("="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Added: {added}")
    print(f"Skipped: {skipped}")
    print(f"Errors: {errors}")
    
    if added > 0:
        print()
        print("Committing changes...")
        conn.commit()
        print("Changes committed!")
    else:
        print()
        print("No changes to commit")
    
    conn.close()
    
    print()
    print("="*70)
    print("DONE")
    print("="*70)

if __name__ == "__main__":
    add_columns()