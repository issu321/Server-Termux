from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for
from flask_login import login_required, current_user
from database.models.company import Company
from database.models.company_payments import CompanyPayments
from database.models.theme_preference import ThemePreference
from database.models.user import User
from services.company_service import CompanyService
from security.password_hash import hash_password
from database.db import db
from config.themes import THEMES

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    company = Company.query.get(company_id)
    payments = CompanyPayments.query.filter_by(company_id=company_id).first()
    theme_pref = ThemePreference.query.filter_by(user_id=current_user.id).first()
    
    return render_template('settings/settings.html',
                         company=company, payments=payments,
                         theme_pref=theme_pref, themes=THEMES)

@settings_bp.route('/company', methods=['POST'])
@login_required
def update_company():
    company_id = session.get('company_id')
    data = request.form.to_dict()
    
    for key in ['employee_count', 'annual_revenue', 'tax_rate']:
        if key in data:
            try:
                data[key] = float(data[key])
            except:
                pass
    
    CompanyService.update_company(company_id, data)
    flash('Company settings updated!', 'success')
    return redirect(url_for('settings.index'))

@settings_bp.route('/theme', methods=['POST'])
@login_required
def update_theme():
    theme_id = request.form.get('theme_id', 'aurora_enterprise')
    session['theme'] = theme_id
    
    theme_pref = ThemePreference.query.filter_by(user_id=current_user.id).first()
    if theme_pref:
        theme_pref.theme_id = theme_id
    else:
        theme_pref = ThemePreference(user_id=current_user.id, theme_id=theme_id)
        db.session.add(theme_pref)
    db.session.commit()
    
    return jsonify({'success': True})

@settings_bp.route('/profile', methods=['POST'])
@login_required
def update_profile():
    current_user.first_name = request.form.get('first_name', current_user.first_name)
    current_user.last_name = request.form.get('last_name', current_user.last_name)
    current_user.email = request.form.get('email', current_user.email)
    
    if request.form.get('new_password'):
        if request.form.get('new_password') == request.form.get('confirm_password'):
            current_user.password_hash = hash_password(request.form.get('new_password'))
            flash('Password updated!', 'success')
        else:
            flash('Passwords do not match', 'danger')
    
    db.session.commit()
    flash('Profile updated!', 'success')
    return redirect(url_for('settings.index'))