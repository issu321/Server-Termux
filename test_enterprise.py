#!/usr/bin/env python3
"""
Test script for Enterprise Service
"""

import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)

from app import create_app
from services.enterprise_service import EnterpriseService

if __name__ == "__main__":
    print("=" * 70)
    print("  TESTING ENTERPRISE FINANCIAL CALCULATIONS")
    print("=" * 70)
    
    app = create_app()
    
    with app.app_context():
        # Calculate metrics for all companies
        success_count = EnterpriseService.calculate_all_companies()
    
    print("\n" + "=" * 70)
    print(f"  COMPLETED: {success_count} companies processed successfully")
    print("=" * 70)
