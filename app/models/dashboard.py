from datetime import datetime, timezone
from ..extensions import db
from sqlalchemy.dialects.postgresql import JSONB

class SavedDashboard(db.Model):
    __tablename__ = 'saved_dashboards'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    dashboard_name = db.Column(db.String(100), nullable=False)
    filters = db.Column(db.JSON, nullable=False, default=dict)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
