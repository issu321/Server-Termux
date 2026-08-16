from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        try:
            seed_initial_data()
        except Exception as e:
            print(f"Seed warning: {e}")

def seed_initial_data():
    """Seed initial data if database is empty."""
    pass