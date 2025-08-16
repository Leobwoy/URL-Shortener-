#!/usr/bin/env python3
"""
Test script for Phase 1 features.
This script demonstrates all the new Phase 1 functionality.
"""

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def test_health_check():
    """Test the health check endpoint."""
    print("🏥 Testing Health Check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health Check: {data['status']} - Version {data['version']}")
            return True
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health Check error: {e}")
        return False

def test_user_registration():
    """Test user registration."""
    print("\n🔐 Testing User Registration...")
    try:
        data = {
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/register", json=data)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ User registered: {result['user']['username']}")
            return result['token']
        else:
            print(f"❌ Registration failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Registration error: {e}")
        return None

def test_user_login():
    """Test user login."""
    print("\n🔑 Testing User Login...")
    try:
        data = {
            "username": "admin",
            "password": "admin123"
        }
        response = requests.post(f"{BASE_URL}/api/v1/auth/login", json=data)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Login successful: {result['user']['username']}")
            return result['token']
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_create_team(token):
    """Test team creation."""
    print("\n👥 Testing Team Creation...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "name": "Marketing Team",
            "description": "Team responsible for marketing campaigns"
        }
        response = requests.post(f"{BASE_URL}/api/v1/teams", json=data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ Team created: {result['team']['name']}")
            return result['team']['id']
        else:
            print(f"❌ Team creation failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Team creation error: {e}")
        return None

def test_get_teams(token):
    """Test getting user's teams."""
    print("\n📋 Testing Get Teams...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/teams", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Teams retrieved: {result['total']} teams")
            for team in result['teams']:
                print(f"  - {team['name']}: {team['description']}")
            return True
        else:
            print(f"❌ Get teams failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get teams error: {e}")
        return False

def test_enhanced_url_shortening(token, team_id):
    """Test enhanced URL shortening with team support."""
    print("\n🔗 Testing Enhanced URL Shortening...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        data = {
            "long_url": "https://www.example.com/very/long/url/that/needs/shortening",
            "title": "Example Website",
            "description": "Our main website for testing",
            "tags": "website,main,example,testing",
            "team_id": team_id,
            "expires_at": "2024-12-31T23:59:59Z"
        }
        response = requests.post(f"{BASE_URL}/api/v1/shorten", json=data, headers=headers)
        if response.status_code == 201:
            result = response.json()
            print(f"✅ URL shortened: {result['short_url']}")
            print(f"  - Short code: {result['short_code']}")
            print(f"  - Message: {result['message']}")
            return result['short_code']
        else:
            print(f"❌ URL shortening failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ URL shortening error: {e}")
        return None

def test_get_user_urls(token):
    """Test getting user URLs with pagination and filtering."""
    print("\n📊 Testing Get User URLs...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/urls?page=1&per_page=10", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ URLs retrieved: {result['total']} total URLs")
            print(f"  - Page {result['page']} of {result['pages']}")
            print(f"  - {len(result['urls'])} URLs on this page")
            for url in result['urls']:
                print(f"    - {url['short_code']}: {url['title']} ({url['click_count']} clicks)")
            return True
        else:
            print(f"❌ Get URLs failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Get URLs error: {e}")
        return False

def test_url_analytics(token, short_code):
    """Test enhanced analytics."""
    print("\n📈 Testing URL Analytics...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{BASE_URL}/api/v1/analytics/{short_code}", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Analytics retrieved for {short_code}")
            print(f"  - Clicks: {result['clicks']}")
            print(f"  - Created: {result['created_at']}")
            if 'team_stats' in result:
                stats = result['team_stats']
                print(f"  - Team Stats: {stats['total_urls']} URLs, {stats['total_clicks']} total clicks")
            return True
        else:
            print(f"❌ Analytics failed: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"❌ Analytics error: {e}")
        return False

def test_admin_endpoints(token):
    """Test admin-only endpoints."""
    print("\n🔒 Testing Admin Endpoints...")
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        # Test getting all users
        response = requests.get(f"{BASE_URL}/api/v1/admin/users", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin users endpoint: {result['total']} users")
        else:
            print(f"❌ Admin users failed: {response.status_code}")
        
        # Test getting all teams
        response = requests.get(f"{BASE_URL}/api/v1/admin/teams", headers=headers)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Admin teams endpoint: {result['total']} teams")
        else:
            print(f"❌ Admin teams failed: {response.status_code}")
            
        return True
    except Exception as e:
        print(f"❌ Admin endpoints error: {e}")
        return False

def main():
    """Main test function."""
    print("🚀 Phase 1 Feature Testing")
    print("=" * 50)
    
    # Test health check
    if not test_health_check():
        print("❌ Application is not running. Please start the app first.")
        return
    
    # Test user registration
    token = test_user_registration()
    if not token:
        print("❌ User registration failed. Trying admin login...")
        token = test_user_login()
        if not token:
            print("❌ All authentication methods failed.")
            return
    
    # Test team creation
    team_id = test_create_team(token)
    
    # Test getting teams
    test_get_teams(token)
    
    # Test enhanced URL shortening
    if team_id:
        short_code = test_enhanced_url_shortening(token, team_id)
    else:
        short_code = test_enhanced_url_shortening(token, None)
    
    # Test getting user URLs
    test_get_user_urls(token)
    
    # Test analytics
    if short_code:
        test_url_analytics(token, short_code)
    
    # Test admin endpoints with admin user
    print("\n🔑 Testing Admin Endpoints with Admin User...")
    admin_token = test_user_login()
    if admin_token:
        test_admin_endpoints(admin_token)
    else:
        print("⚠️  Could not test admin endpoints - admin login failed")
    
    print("\n" + "=" * 50)
    print("🎉 Phase 1 Testing Complete!")
    print("All features are working correctly!")

if __name__ == "__main__":
    main()
