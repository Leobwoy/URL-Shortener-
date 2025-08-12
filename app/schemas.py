from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import validators

class URLSchema(Schema):
    """Schema for URL creation and updates."""
    long_url = fields.Str(required=True, validate=validate.Length(min=1, max=2048))
    expires_at = fields.DateTime(allow_none=True)
    
    def validate_long_url(self, value):
        """Custom validation for URL format."""
        if not validators.url(value):
            raise ValidationError('Invalid URL format')
        return value

class URLResponseSchema(Schema):
    """Schema for URL response."""
    id = fields.Int(dump_only=True)
    long_url = fields.Str(required=True)
    short_code = fields.Str(required=True)
    click_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)

class ShortenRequestSchema(Schema):
    """Schema for URL shortening request."""
    long_url = fields.Str(required=True, validate=validate.Length(min=1, max=2048))
    expires_at = fields.DateTime(allow_none=True)
    
    def validate_long_url(self, value):
        """Custom validation for URL format."""
        if not validators.url(value):
            raise ValidationError('Invalid URL format')
        return value

class ShortenResponseSchema(Schema):
    """Schema for URL shortening response."""
    short_url = fields.Str(required=True)

class AnalyticsSchema(Schema):
    """Schema for analytics response."""
    short_code = fields.Str(required=True)
    clicks = fields.Int(required=True)

class URLListSchema(Schema):
    """Schema for list of URLs."""
    urls = fields.Nested(URLResponseSchema, many=True)
    total = fields.Int()
