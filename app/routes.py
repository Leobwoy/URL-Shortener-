from flask import Blueprint, request, jsonify, redirect, current_app
from marshmallow import ValidationError
from app.models import URL, User, Team, TeamMember, db
from app.schemas import (
    ShortenRequestSchema, ShortenResponseSchema, URLResponseSchema,
    URLUpdateSchema, URLListSchema, AnalyticsSchema, UserSchema,
    UserResponseSchema, UserLoginSchema, TeamSchema, TeamResponseSchema,
    TeamMemberSchema, TeamMemberResponseSchema, ErrorSchema, SuccessSchema
)
from app.auth import (
    login_required, admin_required, team_member_required, team_admin_required,
    hash_password, verify_password, generate_token, get_current_user
)
from app.utils import generate_unique_short_code, get_base_url
from datetime import datetime
import re

# Create versioned blueprints
api_v1 = Blueprint('api_v1', __name__, url_prefix='/api/v1')

# ============================================================================
# AUTHENTICATION ENDPOINTS
# ============================================================================

@api_v1.route('/auth/register', methods=['POST'])
def register():
    """Register a new user."""
    try:
        schema = UserSchema()
        data = schema.load(request.json)
        
        # Check if username or email already exists
        if User.query.filter_by(username=data['username']).first():
            return jsonify({
                'error': 'Registration Failed',
                'message': 'Username already exists'
            }), 409
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({
                'error': 'Registration Failed',
                'message': 'Email already exists'
            }), 409
        
        # Create new user
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=hash_password(data['password'])
        )
        
        db.session.add(user)
        db.session.commit()
        
        # Generate token
        token = generate_token(user.id, user.username)
        
        return jsonify({
            'message': 'User registered successfully',
            'user': UserResponseSchema().dump(user),
            'token': token
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Registration Error',
            'message': str(e)
        }), 500

@api_v1.route('/auth/login', methods=['POST'])
def login():
    """Authenticate user and return JWT token."""
    try:
        schema = UserLoginSchema()
        data = schema.load(request.json)
        
        # Find user by username
        user = User.query.filter_by(username=data['username']).first()
        
        if not user or not verify_password(data['password'], user.password_hash):
            return jsonify({
                'error': 'Authentication Failed',
                'message': 'Invalid username or password'
            }), 401
        
        if not user.is_active:
            return jsonify({
                'error': 'Account Disabled',
                'message': 'Your account has been deactivated'
            }), 403
        
        # Generate token
        token = generate_token(user.id, user.username)
        
        return jsonify({
            'message': 'Login successful',
            'user': UserResponseSchema().dump(user),
            'token': token
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422
    except Exception as e:
        return jsonify({
            'error': 'Login Error',
            'message': str(e)
        }), 500

@api_v1.route('/auth/profile', methods=['GET'])
@login_required
def get_profile():
    """Get current user's profile."""
    user = get_current_user()
    return jsonify({
        'user': UserResponseSchema().dump(user)
    }), 200

# ============================================================================
# TEAM MANAGEMENT ENDPOINTS
# ============================================================================

@api_v1.route('/teams', methods=['POST'])
@login_required
def create_team():
    """Create a new team."""
    try:
        schema = TeamSchema()
        data = schema.load(request.json)
        
        user = get_current_user()
        
        # Create team
        team = Team(
            name=data['name'],
            description=data.get('description')
        )
        db.session.add(team)
        db.session.flush()  # Get team ID
        
        # Add creator as admin
        member = TeamMember(
            user_id=user.id,
            team_id=team.id,
            role='admin'
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Team created successfully',
            'team': TeamResponseSchema().dump(team)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Team Creation Error',
            'message': str(e)
        }), 500

@api_v1.route('/teams', methods=['GET'])
@login_required
def get_teams():
    """Get teams for current user."""
    user = get_current_user()
    
    # Get user's teams
    memberships = TeamMember.query.filter_by(user_id=user.id).all()
    teams = [membership.team for membership in memberships if membership.team.is_active]
    
    return jsonify({
        'teams': [TeamResponseSchema().dump(team) for team in teams],
        'total': len(teams)
    }), 200

@api_v1.route('/teams/<int:team_id>', methods=['GET'])
@team_member_required()
def get_team(team_id):
    """Get team details."""
    team = Team.query.get_or_404(team_id)
    return jsonify({
        'team': TeamResponseSchema().dump(team)
    }), 200

@api_v1.route('/teams/<int:team_id>/members', methods=['POST'])
@team_admin_required()
def add_team_member(team_id):
    """Add a member to a team."""
    try:
        schema = TeamMemberSchema()
        data = schema.load(request.json)
        
        # Check if user exists
        user = User.query.get(data['user_id'])
        if not user:
            return jsonify({
                'error': 'User Not Found',
                'message': 'User does not exist'
            }), 404
        
        # Check if already a member
        existing = TeamMember.query.filter_by(
            user_id=data['user_id'],
            team_id=team_id
        ).first()
        
        if existing:
            return jsonify({
                'error': 'Already Member',
                'message': 'User is already a member of this team'
            }), 409
        
        # Add member
        member = TeamMember(
            user_id=data['user_id'],
            team_id=team_id,
            role=data['role']
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Team member added successfully',
            'member': TeamMemberResponseSchema().dump(member)
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Add Member Error',
            'message': str(e)
        }), 500

# ============================================================================
# ENHANCED URL MANAGEMENT ENDPOINTS
# ============================================================================

@api_v1.route('/shorten', methods=['POST'])
@login_required
def shorten_url():
    """Shorten a URL with team collaboration support."""
    try:
        schema = ShortenRequestSchema()
        data = schema.load(request.json)
        
        user = get_current_user()
        
        # Check if URL already exists for this user/team
        existing_url = URL.query.filter_by(
            long_url=data['long_url'],
            user_id=user.id,
            team_id=data.get('team_id')
        ).first()
        
        if existing_url:
            return jsonify({
                'short_url': f"{get_base_url()}/{existing_url.short_code}",
                'short_code': existing_url.short_code,
                'message': 'URL already shortened'
            }), 200
        
        # Generate unique short code
        short_code = generate_unique_short_code()
        
        # Create URL
        url = URL(
            long_url=data['long_url'],
            short_code=short_code,
            user_id=user.id,
            team_id=data.get('team_id'),
            title=data.get('title'),
            description=data.get('description'),
            tags=data.get('tags'),
            expires_at=data.get('expires_at')
        )
        
        db.session.add(url)
        db.session.commit()
        
        return jsonify({
            'short_url': f"{get_base_url()}/{short_code}",
            'short_code': short_code,
            'message': 'URL shortened successfully'
        }), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'URL Shortening Error',
            'message': str(e)
        }), 500

@api_v1.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    """Redirect to original URL."""
    url = URL.query.filter_by(short_code=short_code, is_active=True).first()
    
    if not url:
        return jsonify({
            'error': 'Not Found',
            'message': 'Short URL not found'
        }), 404
    
    if url.is_expired():
        return jsonify({
            'error': 'Gone',
            'message': 'This URL has expired'
        }), 410
    
    # Increment click count
    url.increment_clicks()
    
    return redirect(url.long_url, code=302)

@api_v1.route('/urls', methods=['GET'])
@login_required
def get_urls():
    """Get URLs for current user with pagination and team filtering."""
    user = get_current_user()
    
    # Get query parameters
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 20, type=int), 100)
    team_id = request.args.get('team_id', type=int)
    search = request.args.get('search', '')
    
    # Build query
    query = URL.query.filter_by(user_id=user.id, is_active=True)
    
    if team_id:
        query = query.filter_by(team_id=team_id)
    
    if search:
        search_filter = f"%{search}%"
        query = query.filter(
            db.or_(
                URL.title.ilike(search_filter),
                URL.description.ilike(search_filter),
                URL.tags.ilike(search_filter)
            )
        )
    
    # Paginate results
    pagination = query.order_by(URL.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    urls = [URLResponseSchema().dump(url) for url in pagination.items]
    
    return jsonify({
        'urls': urls,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200

@api_v1.route('/urls/<short_code>', methods=['GET'])
@login_required
def get_url(short_code):
    """Get specific URL details."""
    user = get_current_user()
    
    url = URL.query.filter_by(
        short_code=short_code,
        user_id=user.id,
        is_active=True
    ).first()
    
    if not url:
        return jsonify({
            'error': 'Not Found',
            'message': 'URL not found'
        }), 404
    
    return jsonify({
        'url': URLResponseSchema().dump(url)
    }), 200

@api_v1.route('/urls/<short_code>', methods=['PUT'])
@login_required
def update_url(short_code):
    """Update URL details."""
    try:
        schema = URLUpdateSchema()
        data = schema.load(request.json)
        
        user = get_current_user()
        
        url = URL.query.filter_by(
            short_code=short_code,
            user_id=user.id,
            is_active=True
        ).first()
        
        if not url:
            return jsonify({
                'error': 'Not Found',
                'message': 'URL not found'
            }), 404
        
        # Update fields
        for field, value in data.items():
            if value is not None:
                setattr(url, field, value)
        
        url.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'URL updated successfully',
            'url': URLResponseSchema().dump(url)
        }), 200
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'error': 'Update Error',
            'message': str(e)
        }), 500

@api_v1.route('/urls/<short_code>', methods=['DELETE'])
@login_required
def delete_url(short_code):
    """Delete a URL (soft delete)."""
    user = get_current_user()
    
    url = URL.query.filter_by(
        short_code=short_code,
        user_id=user.id,
        is_active=True
    ).first()
    
    if not url:
        return jsonify({
            'error': 'Not Found',
            'message': 'URL not found'
        }), 404
    
    # Soft delete
    url.is_active = False
    url.updated_at = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'URL deleted successfully'
    }), 200

@api_v1.route('/analytics/<short_code>', methods=['GET'])
@login_required
def get_analytics(short_code):
    """Get analytics for a URL."""
    user = get_current_user()
    
    url = URL.query.filter_by(
        short_code=short_code,
        user_id=user.id,
        is_active=True
    ).first()
    
    if not url:
        return jsonify({
            'error': 'Not Found',
            'message': 'URL not found'
        }), 404
    
    # Basic analytics
    analytics = {
        'short_code': url.short_code,
        'clicks': url.click_count,
        'created_at': url.created_at.isoformat() if url.created_at else None,
        'last_click': url.updated_at.isoformat() if url.updated_at else None
    }
    
    # Team stats if applicable
    if url.team_id:
        team_urls = URL.query.filter_by(team_id=url.team_id, is_active=True).all()
        total_team_clicks = sum(u.click_count for u in team_urls)
        analytics['team_stats'] = {
            'total_urls': len(team_urls),
            'total_clicks': total_team_clicks,
            'team_rank': sorted(team_urls, key=lambda x: x.click_count, reverse=True).index(url) + 1
        }
    
    return jsonify(analytics), 200

# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@api_v1.route('/admin/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users (admin only)."""
    users = User.query.all()
    return jsonify({
        'users': [UserResponseSchema().dump(user) for user in users],
        'total': len(users)
    }), 200

@api_v1.route('/admin/teams', methods=['GET'])
@admin_required
def get_all_teams():
    """Get all teams (admin only)."""
    teams = Team.query.all()
    return jsonify({
        'teams': [TeamResponseSchema().dump(team) for team in teams],
        'total': len(teams)
    }), 200

# ============================================================================
# LEGACY ENDPOINTS (for backward compatibility)
# ============================================================================

@api_v1.route('/urls/legacy', methods=['GET'])
def get_all_urls_legacy():
    """Legacy endpoint to get all URLs (no auth required)."""
    urls = URL.query.filter_by(is_active=True).all()
    return jsonify({
        'urls': [URLResponseSchema().dump(url) for url in urls],
        'total': len(urls)
    }), 200
