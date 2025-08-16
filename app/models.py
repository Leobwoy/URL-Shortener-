from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app import db

class User(db.Model):
    """User model for authentication and team management."""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    teams = relationship('TeamMember', back_populates='user')
    urls = relationship('URL', back_populates='user')
    
    def to_dict(self):
        """Convert user to dictionary."""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'is_active': self.is_active,
            'is_admin': self.is_admin,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Team(db.Model):
    """Team model for organization and collaboration."""
    __tablename__ = 'teams'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    members = relationship('TeamMember', back_populates='team')
    urls = relationship('URL', back_populates='team')
    
    def to_dict(self):
        """Convert team to dictionary."""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class TeamMember(db.Model):
    """Team membership model with roles."""
    __tablename__ = 'team_members'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=False)
    role = Column(String(20), default='member')  # admin, moderator, member
    joined_at = Column(DateTime, default=func.now())
    
    # Relationships
    user = relationship('User', back_populates='teams')
    team = relationship('Team', back_populates='members')
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('user_id', 'team_id', name='unique_user_team'),
    )
    
    def to_dict(self):
        """Convert team member to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'role': self.role,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None,
            'user': self.user.to_dict() if self.user else None,
            'team': self.team.to_dict() if self.team else None
        }

class URL(db.Model):
    """URL model with team and user associations."""
    __tablename__ = 'urls'
    
    id = Column(Integer, primary_key=True)
    long_url = Column(Text, nullable=False)
    short_code = Column(String(10), unique=True, nullable=False)
    click_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # New fields for team collaboration
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    team_id = Column(Integer, ForeignKey('teams.id'), nullable=True)
    title = Column(String(200))  # Custom title for the URL
    description = Column(Text)   # Description of the URL
    tags = Column(Text)          # Comma-separated tags
    is_active = Column(Boolean, default=True)
    
    # Relationships
    user = relationship('User', back_populates='urls')
    team = relationship('Team', back_populates='urls')
    
    def to_dict(self):
        """Convert URL to dictionary."""
        return {
            'id': self.id,
            'long_url': self.long_url,
            'short_code': self.short_code,
            'click_count': self.click_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'user_id': self.user_id,
            'team_id': self.team_id,
            'title': self.title,
            'description': self.description,
            'tags': self.tags,
            'is_active': self.is_active
        }
    
    def is_expired(self):
        """Check if URL has expired."""
        if self.expires_at is None:
            return False
        return datetime.utcnow() > self.expires_at
    
    def increment_clicks(self):
        """Increment click count."""
        self.click_count += 1
        self.updated_at = datetime.utcnow()
        db.session.commit()
