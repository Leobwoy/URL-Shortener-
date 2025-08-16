# URL Shortener API v2.0 - Phase 1 Documentation

## 🚀 Overview

This document describes the enhanced URL Shortener API with **Phase 1** features including:
- **User Authentication & Authorization**
- **Team Management & Collaboration**
- **Enhanced URL Management**
- **API Versioning (v1)**
- **Advanced Security Features**

## 🔐 Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Authentication Endpoints

#### 1. User Registration
```http
POST /api/v1/auth/register
Content-Type: application/json

{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "securepassword123"
}
```

**Response (201):**
```json
{
    "message": "User registered successfully",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "is_active": true,
        "is_admin": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 2. User Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
    "username": "johndoe",
    "password": "securepassword123"
}
```

**Response (200):**
```json
{
    "message": "Login successful",
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "is_active": true,
        "is_admin": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    },
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### 3. Get User Profile
```http
GET /api/v1/auth/profile
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "user": {
        "id": 1,
        "username": "johndoe",
        "email": "john@example.com",
        "is_active": true,
        "is_admin": false,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

## 👥 Team Management

### Team Endpoints

#### 1. Create Team
```http
POST /api/v1/teams
Authorization: Bearer <token>
Content-Type: application/json

{
    "name": "Marketing Team",
    "description": "Team responsible for marketing campaigns"
}
```

**Response (201):**
```json
{
    "message": "Team created successfully",
    "team": {
        "id": 1,
        "name": "Marketing Team",
        "description": "Team responsible for marketing campaigns",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 2. Get User's Teams
```http
GET /api/v1/teams
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "teams": [
        {
            "id": 1,
            "name": "Marketing Team",
            "description": "Team responsible for marketing campaigns",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1
}
```

#### 3. Get Team Details
```http
GET /api/v1/teams/{team_id}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "team": {
        "id": 1,
        "name": "Marketing Team",
        "description": "Team responsible for marketing campaigns",
        "is_active": true,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }
}
```

#### 4. Add Team Member
```http
POST /api/v1/teams/{team_id}/members
Authorization: Bearer <token>
Content-Type: application/json

{
    "user_id": 2,
    "team_id": 1,
    "role": "member"
}
```

**Response (201):**
```json
{
    "message": "Team member added successfully",
    "member": {
        "id": 1,
        "user_id": 2,
        "team_id": 1,
        "role": "member",
        "joined_at": "2024-01-01T00:00:00Z",
        "user": {...},
        "team": {...}
    }
}
```

## 🔗 Enhanced URL Management

### URL Endpoints

#### 1. Shorten URL (Enhanced)
```http
POST /api/v1/shorten
Authorization: Bearer <token>
Content-Type: application/json

{
    "long_url": "https://www.example.com/very/long/url",
    "title": "Example Website",
    "description": "Our main website",
    "tags": "website,main,example",
    "team_id": 1,
    "expires_at": "2024-12-31T23:59:59Z"
}
```

**Response (201):**
```json
{
    "short_url": "http://localhost:5000/abc123",
    "short_code": "abc123",
    "message": "URL shortened successfully"
}
```

#### 2. Get User URLs (with Pagination & Filtering)
```http
GET /api/v1/urls?page=1&per_page=20&team_id=1&search=marketing
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "urls": [
        {
            "id": 1,
            "long_url": "https://www.example.com",
            "short_code": "abc123",
            "click_count": 15,
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": null,
            "updated_at": "2024-01-01T00:00:00Z",
            "user_id": 1,
            "team_id": 1,
            "title": "Example Website",
            "description": "Our main website",
            "tags": "website,main,example",
            "is_active": true
        }
    ],
    "total": 1,
    "page": 1,
    "per_page": 20,
    "pages": 1
}
```

#### 3. Get Specific URL
```http
GET /api/v1/urls/{short_code}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "url": {
        "id": 1,
        "long_url": "https://www.example.com",
        "short_code": "abc123",
        "click_count": 15,
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": null,
        "updated_at": "2024-01-01T00:00:00Z",
        "user_id": 1,
        "team_id": 1,
        "title": "Example Website",
        "description": "Our main website",
        "tags": "website,main,example",
        "is_active": true
    }
}
```

#### 4. Update URL
```http
PUT /api/v1/urls/{short_code}
Authorization: Bearer <token>
Content-Type: application/json

{
    "title": "Updated Title",
    "description": "Updated description",
    "tags": "updated,tags"
}
```

**Response (200):**
```json
{
    "message": "URL updated successfully",
    "url": {
        "id": 1,
        "long_url": "https://www.example.com",
        "short_code": "abc123",
        "click_count": 15,
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": null,
        "updated_at": "2024-01-01T00:00:00Z",
        "user_id": 1,
        "team_id": 1,
        "title": "Updated Title",
        "description": "Updated description",
        "tags": "updated,tags",
        "is_active": true
    }
}
```

#### 5. Delete URL (Soft Delete)
```http
DELETE /api/v1/urls/{short_code}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "message": "URL deleted successfully"
}
```

#### 6. Get Analytics (Enhanced)
```http
GET /api/v1/analytics/{short_code}
Authorization: Bearer <token>
```

**Response (200):**
```json
{
    "short_code": "abc123",
    "clicks": 15,
    "created_at": "2024-01-01T00:00:00Z",
    "last_click": "2024-01-01T12:00:00Z",
    "team_stats": {
        "total_urls": 5,
        "total_clicks": 150,
        "team_rank": 2
    }
}
```

## 🔒 Admin Endpoints

### Admin-only Endpoints

#### 1. Get All Users
```http
GET /api/v1/admin/users
Authorization: Bearer <admin-token>
```

**Response (200):**
```json
{
    "users": [
        {
            "id": 1,
            "username": "johndoe",
            "email": "john@example.com",
            "is_active": true,
            "is_admin": false,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1
}
```

#### 2. Get All Teams
```http
GET /api/v1/admin/teams
Authorization: Bearer <admin-token>
```

**Response (200):**
```json
{
    "teams": [
        {
            "id": 1,
            "name": "Marketing Team",
            "description": "Team responsible for marketing campaigns",
            "is_active": true,
            "created_at": "2024-01-01T00:00:00Z",
            "updated_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1
}
```

## 🔄 Legacy Endpoints

### Backward Compatibility

#### 1. Get All URLs (Legacy)
```http
GET /api/v1/urls/legacy
```

**Response (200):**
```json
{
    "urls": [
        {
            "id": 1,
            "long_url": "https://www.example.com",
            "short_code": "abc123",
            "click_count": 15,
            "created_at": "2024-01-01T00:00:00Z",
            "expires_at": null,
            "updated_at": "2024-01-01T00:00:00Z",
            "user_id": null,
            "team_id": null,
            "title": null,
            "description": null,
            "tags": null,
            "is_active": true
        }
    ],
    "total": 1
}
```

## 🏥 Health Check

### System Status

#### 1. Health Check
```http
GET /health
```

**Response (200):**
```json
{
    "status": "healthy",
    "version": "2.0.0"
}
```

## 📊 Query Parameters

### Common Query Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `page` | integer | Page number for pagination | 1 |
| `per_page` | integer | Items per page (max 100) | 20 |
| `team_id` | integer | Filter URLs by team | None |
| `search` | string | Search in title, description, tags | None |

### Example Usage

```http
GET /api/v1/urls?page=2&per_page=10&team_id=1&search=marketing
```

## 🚨 Error Responses

### Standard Error Format

```json
{
    "error": "Error Type",
    "message": "Human-readable error message",
    "details": {
        "field_name": ["Specific validation error"]
    },
    "status_code": 400
}
```

### Common HTTP Status Codes

| Status | Description |
|--------|-------------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 409 | Conflict |
| 422 | Validation Error |
| 500 | Internal Server Error |

## 🔐 Role-Based Access Control

### User Roles

| Role | Description | Permissions |
|------|-------------|-------------|
| `member` | Basic team member | View team URLs, create personal URLs |
| `moderator` | Team moderator | Manage team URLs, add/remove members |
| `admin` | Team administrator | Full team management, delete team |
| `system_admin` | System administrator | Access admin endpoints, manage all users/teams |

### Permission Matrix

| Endpoint | Member | Moderator | Admin | System Admin |
|----------|--------|-----------|-------|--------------|
| `/auth/*` | ✅ | ✅ | ✅ | ✅ |
| `/teams` (GET) | ✅ | ✅ | ✅ | ✅ |
| `/teams` (POST) | ✅ | ✅ | ✅ | ✅ |
| `/teams/{id}` | ✅ | ✅ | ✅ | ✅ |
| `/teams/{id}/members` | ❌ | ✅ | ✅ | ✅ |
| `/shorten` | ✅ | ✅ | ✅ | ✅ |
| `/urls` | ✅ | ✅ | ✅ | ✅ |
| `/admin/*` | ❌ | ❌ | ❌ | ✅ |

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Environment Variables
```bash
cp env.example .env
# Edit .env with your configuration
```

### 3. Initialize Database
```bash
python -m flask db upgrade
```

### 4. Run the Application
```bash
python app.py
```

### 5. Test Authentication
```bash
# Register a user
curl -X POST http://localhost:5000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'

# Login
curl -X POST http://localhost:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"password123"}'
```

## 🔮 Future Features (Phase 2+)

- **Advanced Analytics & Reporting**
- **Rate Limiting & API Quotas**
- **Webhook Notifications**
- **Bulk Operations**
- **Custom Domains**
- **QR Code Generation**
- **Mobile Applications**

## 📝 Changelog

### v2.0.0 (Phase 1)
- ✅ User authentication with JWT
- ✅ Team management system
- ✅ Enhanced URL management
- ✅ API versioning (v1)
- ✅ Role-based access control
- ✅ CORS support for team collaboration
- ✅ Comprehensive error handling
- ✅ Backward compatibility

### v1.0.0 (Legacy)
- ✅ Basic URL shortening
- ✅ Click tracking
- ✅ URL expiration
- ✅ Simple CRUD operations
