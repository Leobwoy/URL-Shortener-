from marshmallow import Schema, fields, validate, ValidationError
from datetime import datetime
import validators

# User Schemas
class UserSchema(Schema):
    """Schema for user data."""
    username = fields.Str(required=True, validate=validate.Length(min=3, max=80))
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=6))
    is_admin = fields.Bool(dump_only=True)

class UserResponseSchema(Schema):
    """Schema for user response data."""
    id = fields.Int(dump_only=True)
    username = fields.Str()
    email = fields.Str()
    is_active = fields.Bool()
    is_admin = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class UserLoginSchema(Schema):
    """Schema for user login."""
    username = fields.Str(required=True)
    password = fields.Str(required=True)

# Team Schemas
class TeamSchema(Schema):
    """Schema for team data."""
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))

class TeamResponseSchema(Schema):
    """Schema for team response data."""
    id = fields.Int(dump_only=True)
    name = fields.Str()
    description = fields.Str()
    is_active = fields.Bool()
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)

class TeamMemberSchema(Schema):
    """Schema for team member data."""
    user_id = fields.Int(required=True)
    team_id = fields.Int(required=True)
    role = fields.Str(validate=validate.OneOf(['admin', 'moderator', 'member']))

class TeamMemberResponseSchema(Schema):
    """Schema for team member response data."""
    id = fields.Int(dump_only=True)
    user_id = fields.Int()
    team_id = fields.Int()
    role = fields.Str()
    joined_at = fields.DateTime(dump_only=True)
    user = fields.Nested(UserResponseSchema)
    team = fields.Nested(TeamResponseSchema)

# Enhanced URL Schemas
class ShortenRequestSchema(Schema):
    """Schema for URL shortening request."""
    long_url = fields.Url(required=True)
    expires_at = fields.DateTime(allow_none=True)
    title = fields.Str(validate=validate.Length(max=200))
    description = fields.Str(validate=validate.Length(max=1000))
    tags = fields.Str(validate=validate.Length(max=500))
    team_id = fields.Int(allow_none=True)

class ShortenResponseSchema(Schema):
    """Schema for URL shortening response."""
    short_url = fields.Str()
    short_code = fields.Str()
    message = fields.Str()

class URLSchema(Schema):
    """Schema for URL data."""
    long_url = fields.Url(required=True)
    short_code = fields.Str(dump_only=True)
    click_count = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)
    expires_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime(dump_only=True)
    user_id = fields.Int(allow_none=True)
    team_id = fields.Int(allow_none=True)
    title = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    tags = fields.Str(allow_none=True)
    is_active = fields.Bool()

class URLResponseSchema(Schema):
    """Schema for URL response data."""
    id = fields.Int(dump_only=True)
    long_url = fields.Url()
    short_code = fields.Str()
    click_count = fields.Int()
    created_at = fields.DateTime()
    expires_at = fields.DateTime(allow_none=True)
    updated_at = fields.DateTime()
    user_id = fields.Int(allow_none=True)
    team_id = fields.Int(allow_none=True)
    title = fields.Str(allow_none=True)
    description = fields.Str(allow_none=True)
    tags = fields.Str(allow_none=True)
    is_active = fields.Bool()

class URLUpdateSchema(Schema):
    """Schema for URL updates."""
    long_url = fields.Url(allow_none=True)
    expires_at = fields.DateTime(allow_none=True)
    title = fields.Str(allow_none=True, validate=validate.Length(max=200))
    description = fields.Str(allow_none=True, validate=validate.Length(max=1000))
    tags = fields.Str(allow_none=True, validate=validate.Length(max=500))
    is_active = fields.Bool(allow_none=True)

class URLListSchema(Schema):
    """Schema for URL list response."""
    urls = fields.Nested(URLResponseSchema, many=True)
    total = fields.Int()
    page = fields.Int()
    per_page = fields.Int()

class AnalyticsSchema(Schema):
    """Schema for analytics response."""
    short_code = fields.Str()
    clicks = fields.Int()
    created_at = fields.DateTime()
    last_click = fields.DateTime(allow_none=True)
    team_stats = fields.Dict(allow_none=True)

# Error Schemas
class ErrorSchema(Schema):
    """Schema for error responses."""
    error = fields.Str()
    message = fields.Str()
    details = fields.Dict(allow_none=True)
    status_code = fields.Int()

# Success Schemas
class SuccessSchema(Schema):
    """Schema for success responses."""
    message = fields.Str()
    data = fields.Dict(allow_none=True)
