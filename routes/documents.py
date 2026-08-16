from flask import Blueprint, render_template, request, jsonify, session, flash, redirect, url_for, send_file
from flask_login import login_required, current_user
from database.models.document import Document, Tag
from database.models.company import Company
from database.db import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from security.input_sanitizer import sanitize_filename

documents_bp = Blueprint('documents', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'csv', 'xlsx', 'xls', 'docx', 'txt', 'json', 'xml', 'png', 'jpg', 'jpeg', 'gif', 'zip'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@documents_bp.route('/')
@login_required
def center():
    company_id = session.get('company_id')
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Document.query.filter_by(company_id=company_id, is_deleted=False)
    if category:
        query = query.filter_by(category=category)
    if search:
        query = query.filter(Document.name.contains(search))
    
    documents = query.order_by(Document.created_at.desc()).all()
    tags = Tag.query.filter_by(company_id=company_id).all()
    categories = db.session.query(Document.category).filter_by(company_id=company_id).distinct().all()
    
    return render_template('documents/document_center.html',
                         documents=documents, tags=tags,
                         categories=[c[0] for c in categories if c[0]])

@documents_bp.route('/upload', methods=['POST'])
@login_required
def upload():
    company_id = session.get('company_id')
    
    if 'file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('documents.center'))
    
    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('documents.center'))
    
    if file and allowed_file(file.filename):
        filename = secure_filename(sanitize_filename(file.filename))
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{timestamp}_{filename}"
        
        file_type = filename.rsplit('.', 1)[1].lower()
        upload_dir = os.path.join('uploads', file_type + 's')
        os.makedirs(upload_dir, exist_ok=True)
        
        filepath = os.path.join(upload_dir, unique_filename)
        file.save(filepath)
        
        doc = Document(
            company_id=company_id,
            user_id=current_user.id,
            name=request.form.get('name', filename),
            original_filename=filename,
            file_path=filepath,
            file_type=file_type,
            file_size=os.path.getsize(filepath),
            description=request.form.get('description'),
            category=request.form.get('category'),
            owner=request.form.get('owner', current_user.username)
        )
        db.session.add(doc)
        db.session.commit()
        
        flash('Document uploaded successfully!', 'success')
    else:
        flash('Invalid file type', 'danger')
    
    return redirect(url_for('documents.center'))

@documents_bp.route('/download/<int:doc_id>')
@login_required
def download(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.company_id != session.get('company_id'):
        flash('Access denied', 'danger')
        return redirect(url_for('documents.center'))
    
    if os.path.exists(doc.file_path):
        return send_file(doc.file_path, as_attachment=True, download_name=doc.original_filename)
    flash('File not found', 'danger')
    return redirect(url_for('documents.center'))

@documents_bp.route('/delete/<int:doc_id>', methods=['POST'])
@login_required
def delete(doc_id):
    doc = Document.query.get_or_404(doc_id)
    if doc.company_id != session.get('company_id'):
        return jsonify({'success': False, 'error': 'Access denied'})
    
    doc.is_deleted = True
    doc.deleted_at = datetime.utcnow()
    db.session.commit()
    return jsonify({'success': True})