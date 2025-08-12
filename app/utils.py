import random
import string
from app.models import URL
from app import db

def generate_short_code(length=6):
    """Generate a random alphanumeric short code."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_short_code(length=6):
    """Generate a unique short code that doesn't exist in the database."""
    while True:
        short_code = generate_short_code(length)
        # Check if the short code already exists
        existing_url = URL.query.filter_by(short_code=short_code).first()
        if not existing_url:
            return short_code

def get_base_url():
    """Get the base URL for the application."""
    # In production, this should be set via environment variable
    return 'http://localhost:5000'

def create_short_url(short_code):
    """Create a complete short URL from a short code."""
    base_url = get_base_url()
    return f"{base_url}/{short_code}"

def find_or_create_url(long_url, expires_at=None):
    """Find existing URL or create a new one."""
    # Check if URL already exists
    existing_url = URL.query.filter_by(long_url=long_url).first()
    if existing_url:
        return existing_url
    
    # Create new URL
    short_code = generate_unique_short_code()
    new_url = URL(
        long_url=long_url,
        short_code=short_code,
        expires_at=expires_at
    )
    
    db.session.add(new_url)
    db.session.commit()
    
    return new_url
