from flask import Blueprint, request, jsonify, redirect, abort
from marshmallow import ValidationError
from app.models import URL
from app.schemas import (
    ShortenRequestSchema, ShortenResponseSchema, URLResponseSchema,
    AnalyticsSchema, URLListSchema, URLSchema
)
from app.utils import find_or_create_url, create_short_url
from app import db
from datetime import datetime

api_bp = Blueprint('api', __name__)

# Schema instances
shorten_request_schema = ShortenRequestSchema()
shorten_response_schema = ShortenResponseSchema()
url_response_schema = URLResponseSchema()
analytics_schema = AnalyticsSchema()
url_list_schema = URLListSchema()
url_schema = URLSchema()

@api_bp.route('/shorten', methods=['POST'])
def shorten_url():
    """Shorten a long URL."""
    try:
        # Validate input
        data = shorten_request_schema.load(request.get_json())
        
        # Parse expiration date if provided
        expires_at = None
        if 'expires_at' in data and data['expires_at']:
            expires_at = data['expires_at']
        
        # Find or create URL
        url_obj = find_or_create_url(data['long_url'], expires_at)
        
        # Create response
        short_url = create_short_url(url_obj.short_code)
        response_data = {'short_url': short_url}
        
        return jsonify(response_data), 201
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422

@api_bp.route('/<short_code>', methods=['GET'])
def redirect_to_url(short_code):
    """Redirect to the original URL."""
    # Find URL by short code
    url_obj = URL.query.filter_by(short_code=short_code).first()
    
    if not url_obj:
        abort(404)
    
    # Check if URL has expired
    if url_obj.is_expired():
        abort(410)
    
    # Increment click count
    url_obj.increment_clicks()
    
    # Redirect to original URL
    return redirect(url_obj.long_url, code=302)

@api_bp.route('/urls', methods=['GET'])
def get_all_urls():
    """Get all stored URLs."""
    urls = URL.query.all()
    url_data = [url.to_dict() for url in urls]
    
    response_data = {
        'urls': url_data,
        'total': len(url_data)
    }
    
    return jsonify(response_data)

@api_bp.route('/urls/<short_code>', methods=['GET'])
def get_url(short_code):
    """Get a specific URL by short code."""
    url_obj = URL.query.filter_by(short_code=short_code).first()
    
    if not url_obj:
        abort(404)
    
    return jsonify(url_obj.to_dict())

@api_bp.route('/urls/<short_code>', methods=['PUT'])
def update_url(short_code):
    """Update a URL's destination."""
    try:
        # Find URL
        url_obj = URL.query.filter_by(short_code=short_code).first()
        
        if not url_obj:
            abort(404)
        
        # Validate input
        data = url_schema.load(request.get_json())
        
        # Update URL
        url_obj.long_url = data['long_url']
        if 'expires_at' in data:
            url_obj.expires_at = data['expires_at']
        
        db.session.commit()
        
        return jsonify(url_obj.to_dict())
        
    except ValidationError as e:
        return jsonify({
            'error': 'Validation Error',
            'message': 'Invalid input data',
            'details': e.messages
        }), 422

@api_bp.route('/urls/<short_code>', methods=['DELETE'])
def delete_url(short_code):
    """Delete a URL."""
    url_obj = URL.query.filter_by(short_code=short_code).first()
    
    if not url_obj:
        abort(404)
    
    db.session.delete(url_obj)
    db.session.commit()
    
    return jsonify({
        'message': 'URL deleted successfully'
    }), 200

@api_bp.route('/analytics/<short_code>', methods=['GET'])
def get_analytics(short_code):
    """Get analytics for a specific URL."""
    url_obj = URL.query.filter_by(short_code=short_code).first()
    
    if not url_obj:
        abort(404)
    
    analytics_data = {
        'short_code': short_code,
        'clicks': url_obj.click_count
    }
    
    return jsonify(analytics_data)
