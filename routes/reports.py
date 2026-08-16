from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, send_file, current_app
from flask_login import login_required, current_user
from database.models.report import Report
from services.report_service import ReportService
from config.constants import REPORT_TYPES, REPORT_LABELS, CURRENCY_SYMBOLS
from database.db import db
from datetime import datetime
import os

reports_bp = Blueprint('reports', __name__)

def _get_currency_symbol():
    """Get currency symbol from session or fallback to CURRENCY_SYMBOLS."""
    if 'currency_symbol' in session:
        return session['currency_symbol']
    currency = session.get('company_currency', 'USD')
    return CURRENCY_SYMBOLS.get(currency, '$')

@reports_bp.route('/')
@login_required
def center():
    company_id = session.get('company_id')
    reports = Report.query.filter_by(company_id=company_id).order_by(Report.created_at.desc()).all()
    currency_symbol = _get_currency_symbol()
    return render_template('reports/report_center.html', 
                         reports=reports,
                         report_types=REPORT_TYPES,
                         report_labels=REPORT_LABELS,
                         report_configs=ReportService.REPORT_TYPE_CONFIG,
                         currency_symbol=currency_symbol)

@reports_bp.route('/generate', methods=['POST'])
@login_required
def generate():
    company_id = session.get('company_id')
    report_type = request.form.get('report_type', 'executive')
    name = request.form.get('name', '').strip()
    format_type = request.form.get('format', 'pdf')
    currency_symbol = _get_currency_symbol()
    
    if not name:
        name = f"{REPORT_LABELS.get(report_type, 'Report')} - {datetime.now().strftime('%Y-%m-%d')}"
    
    report = ReportService.generate_report(
        company_id, current_user.id, report_type, name, format_type, currency_symbol=currency_symbol
    )
    
    if report.file_path and os.path.exists(report.file_path):
        flash(f'Report "{name}" generated successfully as {format_type.upper()}!', 'success')
    else:
        flash(f'Report generation failed: {report.summary}', 'danger')
    return redirect(url_for('reports.center'))

@reports_bp.route('/download/<int:report_id>')
@login_required
def download(report_id):
    report = Report.query.get_or_404(report_id)
    if report.company_id != session.get('company_id'):
        flash('Access denied', 'danger')
        return redirect(url_for('reports.center'))
    
    if not report.file_path:
        flash('Report file not available', 'danger')
        return redirect(url_for('reports.center'))
    
    # Resolve file path - handle both relative and absolute paths
    file_path = report.file_path
    if not os.path.isabs(file_path):
        file_path = os.path.join(current_app.root_path, file_path)
    
    # If file doesn't exist, try to regenerate it on-the-fly
    if not os.path.exists(file_path):
        try:
            new_path = ReportService.generate_file_for_report(report)
            report.file_path = new_path
            report.last_generated = datetime.utcnow()
            if os.path.exists(new_path):
                report.file_size = os.path.getsize(new_path)
            db.session.commit()
            file_path = new_path
            if not os.path.isabs(file_path):
                file_path = os.path.join(current_app.root_path, file_path)
        except Exception as e:
            flash(f'File not found and regeneration failed: {str(e)}', 'danger')
            return redirect(url_for('reports.center'))
    
    if os.path.exists(file_path):
        filename = os.path.basename(file_path)
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    
    flash('File not found', 'danger')
    return redirect(url_for('reports.center'))

@reports_bp.route('/view/<report_type>')
@login_required
def view(report_type):
    currency_symbol = _get_currency_symbol()
    return render_template(f'reports/{report_type}_report.html', report_type=report_type, currency_symbol=currency_symbol)