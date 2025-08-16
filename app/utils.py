import random
import string
from app.models import URL, db

def generate_short_code(length=6):
    """Generate a random short code."""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def generate_unique_short_code(length=6):
    """Generate a unique short code."""
    while True:
        short_code = generate_short_code(length)
        if not URL.query.filter_by(short_code=short_code).first():
            return short_code

def get_base_url():
    """Get the base URL for the application."""
    from flask import current_app, request
    if current_app.config.get('BASE_URL'):
        return current_app.config['BASE_URL']
    return request.host_url.rstrip('/')

def create_short_url(short_code):
    """Create a full short URL."""
    return f"{get_base_url()}/{short_code}"

def find_or_create_url(long_url, expires_at=None, user_id=None, team_id=None):
    """Find existing URL or create new one."""
    # Check if URL already exists for this user/team combination
    existing_url = URL.query.filter_by(
        long_url=long_url,
        user_id=user_id,
        team_id=team_id
    ).first()
    
    if existing_url:
        return existing_url
    
    # Create new URL
    short_code = generate_unique_short_code()
    url = URL(
        long_url=long_url,
        short_code=short_code,
        expires_at=expires_at,
        user_id=user_id,
        team_id=team_id
    )
    
    db.session.add(url)
    db.session.commit()
    return url

def get_user_urls(user_id, team_id=None, page=1, per_page=20):
    """Get paginated URLs for a user, optionally filtered by team."""
    query = URL.query.filter_by(user_id=user_id, is_active=True)
    
    if team_id:
        query = query.filter_by(team_id=team_id)
    
    return query.order_by(URL.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def get_team_urls(team_id, page=1, per_page=20):
    """Get paginated URLs for a team."""
    return URL.query.filter_by(
        team_id=team_id, 
        is_active=True
    ).order_by(URL.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

def search_urls(user_id, search_term, team_id=None, page=1, per_page=20):
    """Search URLs by title, description, or tags."""
    query = URL.query.filter_by(user_id=user_id, is_active=True)
    
    if team_id:
        query = query.filter_by(team_id=team_id)
    
    if search_term:
        search_filter = f"%{search_term}%"
        query = query.filter(
            db.or_(
                URL.title.ilike(search_filter),
                URL.description.ilike(search_filter),
                URL.tags.ilike(search_filter)
            )
        )
    
    return query.order_by(URL.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
