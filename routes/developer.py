from flask import Blueprint, render_template, jsonify, session
from flask_login import login_required
from database.db import db
from database.models.company import Company
import os
from datetime import datetime

developer_bp = Blueprint('developer', __name__)

@developer_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    company = Company.query.get(company_id)
    
    # System stats
    db_path = 'business_simulator.db'
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0
    
    stats = {
        'db_size_mb': round(db_size / (1024 * 1024), 2),
        'app_version': '1.0.0',
        'build_date': '2025-01-15',
        'python_version': '3.11',
        'flask_version': '3.0.0',
        'total_companies': Company.query.count(),
        'uptime': '99.9%'
    }
    
    return render_template('developer/developer.html', company=company, stats=stats)