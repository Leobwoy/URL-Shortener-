import jwt
import bcrypt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify, current_app
from app.models import User
from app import db

def hash_password(password):
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against its hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def generate_token(user_id, username, expires_in=3600):
    """Generate JWT token for user."""
    payload = {
        'user_id': user_id,
        'username': username,
        'exp': datetime.utcnow() + timedelta(seconds=expires_in),
        'iat': datetime.utcnow()
    }
    secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_token(token):
    """Verify JWT token and return payload."""
    try:
        secret_key = current_app.config.get('SECRET_KEY', 'dev-secret-key')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user():
    """Get current user from JWT token."""
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None
    
    try:
        token = auth_header.split(' ')[1]  # Bearer <token>
        payload = verify_token(token)
        if payload:
            user = User.query.get(payload['user_id'])
            if user and user.is_active:
                return user
    except (IndexError, KeyError):
        pass
    
    return None

def login_required(f):
    """Decorator to require authentication."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                'error': 'Authentication Required',
                'message': 'Valid JWT token is required'
            }), 401
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator to require admin privileges."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user = get_current_user()
        if not user:
            return jsonify({
                'error': 'Authentication Required',
                'message': 'Valid JWT token is required'
            }), 401
        
        if not user.is_admin:
            return jsonify({
                'error': 'Access Denied',
                'message': 'Admin privileges required'
            }), 403
        
        return f(*args, **kwargs)
    return decorated_function

def team_member_required(team_id_param='team_id'):
    """Decorator to require team membership."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({
                    'error': 'Authentication Required',
                    'message': 'Valid JWT token is required'
                }), 401
            
            # Get team_id from kwargs or request
            team_id = kwargs.get(team_id_param)
            if not team_id:
                team_id = request.args.get(team_id_param)
                if not team_id:
                    team_id = request.json.get(team_id_param) if request.is_json else None
            
            if not team_id:
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'{team_id_param} is required'
                }), 400
            
            # Check if user is member of the team
            from app.models import TeamMember
            membership = TeamMember.query.filter_by(
                user_id=user.id,
                team_id=team_id
            ).first()
            
            if not membership:
                return jsonify({
                    'error': 'Access Denied',
                    'message': 'Team membership required'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def team_admin_required(team_id_param='team_id'):
    """Decorator to require team admin privileges."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user = get_current_user()
            if not user:
                return jsonify({
                    'error': 'Authentication Required',
                    'message': 'Valid JWT token is required'
                }), 401
            
            # Get team_id from kwargs or request
            team_id = kwargs.get(team_id_param)
            if not team_id:
                team_id = request.args.get(team_id_param)
                if not team_id:
                    team_id = request.json.get(team_id_param) if request.is_json else None
            
            if not team_id:
                return jsonify({
                    'error': 'Bad Request',
                    'message': f'{team_id_param} is required'
                }), 400
            
            # Check if user is admin of the team
            from app.models import TeamMember
            membership = TeamMember.query.filter_by(
                user_id=user.id,
                team_id=team_id,
                role='admin'
            ).first()
            
            if not membership:
                return jsonify({
                    'error': 'Access Denied',
                    'message': 'Team admin privileges required'
                }), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
