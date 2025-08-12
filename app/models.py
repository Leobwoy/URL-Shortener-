from datetime import datetime
from app import db

class URL(db.Model):
    """URL model for storing shortened URLs."""
    __tablename__ = 'urls'
    
    id = db.Column(db.Integer, primary_key=True)
    long_url = db.Column(db.Text, unique=True, nullable=False)
    short_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    click_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<URL {self.short_code}: {self.long_url}>'
    
    def to_dict(self):
        """Convert model to dictionary."""
        return {
            'id': self.id,
            'long_url': self.long_url,
            'short_code': self.short_code,
            'click_count': self.click_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
    
    def is_expired(self):
        """Check if the URL has expired."""
        if not self.expires_at:
            return False
        return datetime.utcnow() > self.expires_at
    
    def increment_clicks(self):
        """Increment the click count."""
        self.click_count += 1
        db.session.commit()
