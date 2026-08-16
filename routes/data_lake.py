from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required
from database.models.document import Document
from database.models.import_history import ImportHistory
from database.db import db

data_lake_bp = Blueprint('data_lake', __name__)

@data_lake_bp.route('/')
@login_required
def index():
    company_id = session.get('company_id')
    documents = Document.query.filter_by(company_id=company_id, is_deleted=False).count()
    imports = ImportHistory.query.filter_by(company_id=company_id).order_by(ImportHistory.created_at.desc()).limit(20).all()
    return render_template('data_lake/data_lake.html', document_count=documents, imports=imports)