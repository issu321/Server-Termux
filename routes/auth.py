from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from database.db import db
from database.models.user import User
from database.models.company import Company
from database.models.theme_preference import ThemePreference
from services.auth_service import AuthService
from services.company_service import CompanyService
from security.password_hash import hash_password, verify_password
from config.constants import SECURITY_QUESTIONS, CURRENCY_SYMBOLS
import uuid

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.index'))

    # Check if first launch
    if not CompanyService.company_exists():
        return redirect(url_for('auth.setup'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        remember = bool(request.form.get('remember'))

        user, error = AuthService.authenticate(username, password, request.remote_addr)

        if user:
            login_user(user, remember=remember)
            company = Company.query.first()
            if company:
                session['company_id'] = company.id
                session['company_currency'] = company.currency
                session['currency_symbol'] = CURRENCY_SYMBOLS.get(company.currency, '$')
            session['theme'] = 'aurora_enterprise'

            # Load theme preference
            theme_pref = ThemePreference.query.filter_by(user_id=user.id).first()
            if theme_pref:
                session['theme'] = theme_pref.theme_id

            flash(f'Welcome back, {user.username}!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page or url_for('dashboard.index'))
        else:
            flash(error or 'Invalid credentials', 'danger')

    return render_template('auth/login.html')

@auth_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    # Allow creating new company setups anytime — existing data is preserved
    if request.method == 'POST':
        step = int(request.form.get('step', 1))

        if step == 1:
            session['setup_step'] = 2
            return jsonify({'success': True, 'next_step': 2})

        elif step == 2:
            # Company details
            company_data = {
                'company_name': request.form.get('company_name'),
                'business_name': request.form.get('business_name'),
                'owner_name': request.form.get('owner_name'),
                'ceo_name': request.form.get('ceo_name'),
                'industry': request.form.get('industry'),
                'business_type': request.form.get('business_type'),
                'description': request.form.get('description'),
                'company_size': request.form.get('company_size'),
                'employee_count': int(request.form.get('employee_count', 0)),
                'annual_revenue': float(request.form.get('annual_revenue', 0)),
                'currency': request.form.get('currency', 'USD'),
                'country': request.form.get('country'),
                'city': request.form.get('city'),
                'timezone': request.form.get('timezone', 'UTC'),
                'tax_type': request.form.get('tax_type'),
                'tax_rate': float(request.form.get('tax_rate', 0)),
                'email': request.form.get('email'),
                'mobile': request.form.get('mobile'),
                'website': request.form.get('website')
            }
            session['company_data'] = company_data
            return jsonify({'success': True, 'next_step': 3})

        elif step == 3:
            # Payment config
            payment_data = {
                'upi_link': request.form.get('upi_link'),
                'upi_id': request.form.get('upi_id'),
                'bank_account_number': request.form.get('bank_account_number'),
                'bank_ifsc': request.form.get('bank_ifsc'),
                'bank_name': request.form.get('bank_name'),
                'payment_gateway_link': request.form.get('payment_gateway_link'),
                'payment_link': request.form.get('payment_link'),
                'whatsapp_business_link': request.form.get('whatsapp_business_link')
            }
            session['payment_data'] = payment_data
            return jsonify({'success': True, 'next_step': 4})

        elif step == 4:
            # Admin account
            admin_data = {
                'username': request.form.get('username'),
                'email': request.form.get('email'),
                'password': request.form.get('password'),
                'security_question_1': request.form.get('security_question_1'),
                'security_answer_1': request.form.get('security_answer_1'),
                'security_question_2': request.form.get('security_question_2'),
                'security_answer_2': request.form.get('security_answer_2'),
                'security_question_3': request.form.get('security_question_3'),
                'security_answer_3': request.form.get('security_answer_3')
            }
            session['admin_data'] = admin_data
            return jsonify({'success': True, 'next_step': 5})

        elif step == 5:
            recovery_email = request.form.get('recovery_email')
            session['recovery_email'] = recovery_email
            session['recovery_code'] = str(uuid.uuid4())[:8].upper()
            return jsonify({'success': True, 'next_step': 6, 'recovery_code': session['recovery_code']})

        elif step == 6:
            # Finalize - create everything
            try:
                company_data = session.get('company_data', {})
                company = CompanyService.create_company(company_data)

                # Save payments
                payment_data = session.get('payment_data', {})
                CompanyService.save_payments(company.id, payment_data)

                # Create admin
                admin_data = session.get('admin_data', {})
                admin = User(
                    username=admin_data['username'],
                    email=admin_data['email'],
                    first_name=admin_data.get('first_name', 'Admin'),
                    role='Admin',
                    is_admin=True,
                    security_question_1=admin_data.get('security_question_1'),
                    security_answer_1=admin_data.get('security_answer_1'),
                    security_question_2=admin_data.get('security_question_2'),
                    security_answer_2=admin_data.get('security_answer_2'),
                    security_question_3=admin_data.get('security_question_3'),
                    security_answer_3=admin_data.get('security_answer_3')
                )
                admin.password_hash = hash_password(admin_data['password'])
                db.session.add(admin)
                db.session.commit()

                # Create theme preference
                theme = ThemePreference(user_id=admin.id, company_id=company.id, theme_id='aurora_enterprise')
                db.session.add(theme)
                db.session.commit()

                # Login the admin
                login_user(admin)
                session['company_id'] = company.id
                session['company_currency'] = company.currency
                session['currency_symbol'] = CURRENCY_SYMBOLS.get(company.currency, '$')
                session['theme'] = 'aurora_enterprise'
                session.pop('company_data', None)
                session.pop('payment_data', None)
                session.pop('admin_data', None)
                session.pop('recovery_email', None)
                session.pop('recovery_code', None)

                return jsonify({'success': True, 'redirect': url_for('dashboard.index')})
            except Exception as e:
                db.session.rollback()
                return jsonify({'success': False, 'error': str(e)})

    return render_template('auth/register.html', security_questions=SECURITY_QUESTIONS)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Standalone user registration for existing companies."""
    if not CompanyService.company_exists():
        flash('Please complete company setup first.', 'warning')
        return redirect(url_for('auth.setup'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        first_name = request.form.get('first_name', '')
        
        security_question_1 = request.form.get('security_question_1')
        security_answer_1 = request.form.get('security_answer_1')
        security_question_2 = request.form.get('security_question_2')
        security_answer_2 = request.form.get('security_answer_2')
        security_question_3 = request.form.get('security_question_3')
        security_answer_3 = request.form.get('security_answer_3')
        
        # Validation
        if not username or not email or not password:
            flash('Username, email and password are required.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Check existing user
        existing = User.query.filter((User.username == username) | (User.email == email)).first()
        if existing:
            flash('Username or email already exists.', 'danger')
            return redirect(url_for('auth.register'))
        
        # Create user
        user = User(
            username=username,
            email=email,
            first_name=first_name,
            role='Analyst',
            is_admin=False,
            security_question_1=security_question_1,
            security_answer_1=security_answer_1,
            security_question_2=security_question_2,
            security_answer_2=security_answer_2,
            security_question_3=security_question_3,
            security_answer_3=security_answer_3
        )
        user.password_hash = hash_password(password)
        db.session.add(user)
        db.session.commit()
        
        # Create theme preference for new user
        company = Company.query.first()
        if company:
            theme = ThemePreference(user_id=user.id, company_id=company.id, theme_id='aurora_enterprise')
            db.session.add(theme)
            db.session.commit()
        
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', security_questions=SECURITY_QUESTIONS)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('auth.login'))