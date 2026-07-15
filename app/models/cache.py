from datetime import datetime, timezone
from ..extensions import db
from sqlalchemy.dialects.postgresql import JSONB

class CachedRaceData(db.Model):
    __tablename__ = 'cached_race_data'
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.Integer, nullable=False, index=True)
    resource = db.Column(db.String(50), nullable=False)
    data = db.Column(db.JSON, nullable=False)
    fetched_at = db.Column(db.DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    __table_args__ = (db.UniqueConstraint('session_key', 'resource'),)
