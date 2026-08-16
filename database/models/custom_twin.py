from database.db import db
from datetime import datetime
import json

class CustomTwin(db.Model):
    """Model for user-defined custom twins."""
    __tablename__ = 'custom_twins'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Twin metadata
    name = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(100), nullable=False)  # URL-friendly name
    description = db.Column(db.Text)
    icon = db.Column(db.String(50), default='fa-cube')  # FontAwesome icon class
    color = db.Column(db.String(20), default='#00D4FF')  # Theme color
    
    # Field definitions (JSON array of field configs)
    # Each field: {name, label, type, required, default, options}
    field_definitions = db.Column(db.Text, default='[]')
    
    # Stats configuration (JSON array of stat configs)
    # Each stat: {name, label, type, field, formula, color}
    stats_config = db.Column(db.Text, default='[]')
    
    # Display configuration
    table_columns = db.Column(db.Text, default='[]')  # Which fields to show in table
    
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    # Relationships
    records = db.relationship('CustomTwinRecord', backref='twin', lazy='dynamic', cascade='all, delete-orphan')
    
    def get_field_definitions(self):
        """Parse and return field definitions as list."""
        try:
            return json.loads(self.field_definitions) if self.field_definitions else []
        except:
            return []
    
    def set_field_definitions(self, fields):
        """Set field definitions from list."""
        self.field_definitions = json.dumps(fields)
    
    def get_stats_config(self):
        """Parse and return stats configuration as list."""
        try:
            return json.loads(self.stats_config) if self.stats_config else []
        except:
            return []
    
    def set_stats_config(self, stats):
        """Set stats configuration from list."""
        self.stats_config = json.dumps(stats)
    
    def get_table_columns(self):
        """Parse and return table columns as list."""
        try:
            return json.loads(self.table_columns) if self.table_columns else []
        except:
            return []
    
    def set_table_columns(self, columns):
        """Set table columns from list."""
        self.table_columns = json.dumps(columns)
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'icon': self.icon,
            'color': self.color,
            'field_definitions': self.get_field_definitions(),
            'stats_config': self.get_stats_config(),
            'table_columns': self.get_table_columns(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'record_count': self.records.count()
        }


class CustomTwinRecord(db.Model):
    """Model for records in a custom twin."""
    __tablename__ = 'custom_twin_records'
    
    id = db.Column(db.Integer, primary_key=True)
    twin_id = db.Column(db.Integer, db.ForeignKey('custom_twins.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    
    # Record data (JSON object with field values)
    data = db.Column(db.Text, default='{}')
    
    # Metadata
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    
    def get_data(self):
        """Parse and return record data as dict."""
        try:
            return json.loads(self.data) if self.data else {}
        except:
            return {}
    
    def set_data(self, data):
        """Set record data from dict."""
        self.data = json.dumps(data)
    
    def get_field_value(self, field_name, default=None):
        """Get a specific field value."""
        data = self.get_data()
        return data.get(field_name, default)
    
    def set_field_value(self, field_name, value):
        """Set a specific field value."""
        data = self.get_data()
        data[field_name] = value
        self.set_data(data)
    
    def to_dict(self, include_twin=False):
        result = {
            'id': self.id,
            'twin_id': self.twin_id,
            'company_id': self.company_id,
            'data': self.get_data(),
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
        if include_twin and self.twin:
            result['twin'] = self.twin.to_dict()
        return result
