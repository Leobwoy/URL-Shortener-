#!/usr/bin/env python3
"""
Database initialization script for Phase 1 features.
This script creates all the new tables for User, Team, TeamMember, and enhanced URL models.
"""

from app import create_app, db
from app.models import User, Team, TeamMember, URL

def init_database():
    """Initialize the database with all Phase 1 tables."""
    app = create_app('development')
    
    with app.app_context():
        print("Creating database tables...")
        
        # Drop all existing tables to ensure clean slate
        print("Dropping existing tables...")
        db.drop_all()
        
        # Create all tables
        db.create_all()
        
        print("✅ Database tables created successfully!")
        
        # Create a default admin user for testing
        try:
            from app.auth import hash_password
            
            admin_user = User(
                username='admin',
                email='admin@example.com',
                password_hash=hash_password('admin123'),
                is_admin=True
            )
            db.session.add(admin_user)
            db.session.commit()
            print("✅ Default admin user created (username: admin, password: admin123)")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not create admin user: {e}")
        
        # Show table information
        print("\n📊 Database Tables Created:")
        print(f"  - Users: {User.query.count()} records")
        print(f"  - Teams: {Team.query.count()} records")
        print(f"  - Team Members: {TeamMember.query.count()} records")
        print(f"  - URLs: {URL.query.count()} records")
        
        print("\n🚀 Phase 1 database initialization complete!")
        print("You can now run the application with: python app.py")

if __name__ == '__main__':
    init_database()
