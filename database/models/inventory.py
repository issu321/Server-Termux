from database.db import db
from datetime import datetime

class Inventory(db.Model):
    __tablename__ = 'inventory'
    
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=False)
    sku = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    category = db.Column(db.String(100))
    supplier_id = db.Column(db.Integer, db.ForeignKey('suppliers.id'))
    unit_cost = db.Column(db.Float, default=0.0)
    selling_price = db.Column(db.Float, default=0.0)
    quantity_on_hand = db.Column(db.Integer, default=0)
    quantity_reserved = db.Column(db.Integer, default=0)
    quantity_available = db.Column(db.Integer, default=0)
    reorder_point = db.Column(db.Integer, default=0)
    reorder_quantity = db.Column(db.Integer, default=0)
    max_stock = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200))
    branch_id = db.Column(db.Integer, db.ForeignKey('branches.id'))
    is_active = db.Column(db.Boolean, default=True)
    turnover_rate = db.Column(db.Float)
    days_on_hand = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def stock_value(self):
        return self.quantity_on_hand * self.unit_cost
    
    def is_low_stock(self):
        return self.quantity_available <= self.reorder_point
    
    def is_overstock(self):
        return self.max_stock > 0 and self.quantity_on_hand > self.max_stock
    
    def to_dict(self):
        return {
            'id': self.id,
            'company_id': self.company_id,
            'sku': self.sku,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            'supplier_id': self.supplier_id,
            'unit_cost': self.unit_cost,
            'selling_price': self.selling_price,
            'quantity_on_hand': self.quantity_on_hand,
            'quantity_reserved': self.quantity_reserved,
            'quantity_available': self.quantity_available,
            'reorder_point': self.reorder_point,
            'reorder_quantity': self.reorder_quantity,
            'max_stock': self.max_stock,
            'location': self.location,
            'branch_id': self.branch_id,
            'is_active': self.is_active,
            'turnover_rate': self.turnover_rate,
            'days_on_hand': self.days_on_hand,
            'is_low_stock': self.is_low_stock(),
            'is_overstock': self.is_overstock(),
            'stock_value': self.stock_value(),
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class InventoryMovement(db.Model):
    __tablename__ = 'inventory_movements'
    
    id = db.Column(db.Integer, primary_key=True)
    inventory_id = db.Column(db.Integer, db.ForeignKey('inventory.id'), nullable=False)
    movement_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_cost = db.Column(db.Float)
    total_value = db.Column(db.Float)
    reference = db.Column(db.String(200))
    notes = db.Column(db.Text)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    item = db.relationship('Inventory', backref='movements')