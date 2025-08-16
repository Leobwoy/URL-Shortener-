import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import User, Team, TeamMember, URL
from app.auth import hash_password, generate_token

class TestPhase1Features:
    """Test suite for Phase 1 features."""
    
    @pytest.fixture
    def app(self):
        """Create application for testing."""
        app = create_app('testing')
        return app
    
    @pytest.fixture
    def client(self, app):
        """Create test client."""
        return app.test_client()
    
    @pytest.fixture
    def db_session(self, app):
        """Create database session."""
        with app.app_context():
            db.create_all()
            yield db
            db.session.remove()
            db.drop_all()
    
    @pytest.fixture
    def test_user(self, db_session):
        """Create test user."""
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=hash_password('password123')
        )
        db_session.session.add(user)
        db_session.session.commit()
        return user
    
    @pytest.fixture
    def test_team(self, db_session, test_user):
        """Create test team."""
        team = Team(
            name='Test Team',
            description='A test team'
        )
        db_session.session.add(team)
        db_session.session.flush()
        
        member = TeamMember(
            user_id=test_user.id,
            team_id=team.id,
            role='admin'
        )
        db_session.session.add(member)
        db_session.session.commit()
        return team
    
    @pytest.fixture
    def auth_headers(self, test_user):
        """Create authentication headers."""
        token = generate_token(test_user.id, test_user.username)
        return {'Authorization': f'Bearer {token}'}
    
    def test_user_registration(self, client, db_session):
        """Test user registration endpoint."""
        response = client.post('/api/v1/auth/register', json={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'password123'
        })
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'token' in data
        assert data['user']['username'] == 'newuser'
        assert data['user']['email'] == 'new@example.com'
    
    def test_user_login(self, client, db_session, test_user):
        """Test user login endpoint."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'password123'
        })
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'token' in data
        assert data['user']['username'] == 'testuser'
    
    def test_invalid_login(self, client, db_session, test_user):
        """Test invalid login credentials."""
        response = client.post('/api/v1/auth/login', json={
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        assert response.status_code == 401
    
    def test_get_profile(self, client, db_session, test_user, auth_headers):
        """Test getting user profile."""
        response = client.get('/api/v1/auth/profile', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['user']['username'] == 'testuser'
    
    def test_create_team(self, client, db_session, test_user, auth_headers):
        """Test team creation."""
        response = client.post('/api/v1/teams', json={
            'name': 'New Team',
            'description': 'A new test team'
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['team']['name'] == 'New Team'
        assert data['team']['description'] == 'A new test team'
    
    def test_get_user_teams(self, client, db_session, test_user, test_team, auth_headers):
        """Test getting user's teams."""
        response = client.get('/api/v1/teams', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['teams']) == 1
        assert data['teams'][0]['name'] == 'Test Team'
    
    def test_get_team_details(self, client, db_session, test_user, test_team, auth_headers):
        """Test getting team details."""
        response = client.get(f'/api/v1/teams/{test_team.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['team']['name'] == 'Test Team'
    
    def test_add_team_member(self, client, db_session, test_user, test_team, auth_headers):
        """Test adding team member."""
        # Create another user
        new_user = User(
            username='member',
            email='member@example.com',
            password_hash=hash_password('password123')
        )
        db_session.session.add(new_user)
        db_session.session.commit()
        
        response = client.post(f'/api/v1/teams/{test_team.id}/members', json={
            'user_id': new_user.id,
            'team_id': test_team.id,
            'role': 'member'
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['member']['role'] == 'member'
    
    def test_enhanced_url_shortening(self, client, db_session, test_user, test_team, auth_headers):
        """Test enhanced URL shortening with team support."""
        response = client.post('/api/v1/shorten', json={
            'long_url': 'https://www.example.com',
            'title': 'Example Site',
            'description': 'A test website',
            'tags': 'test,example,website',
            'team_id': test_team.id
        }, headers=auth_headers)
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'short_url' in data
        assert 'short_code' in data
    
    def test_get_user_urls_with_pagination(self, client, db_session, test_user, auth_headers):
        """Test getting user URLs with pagination."""
        # Create some test URLs
        for i in range(25):
            url = URL(
                long_url=f'https://example{i}.com',
                short_code=f'code{i:02d}',
                user_id=test_user.id
            )
            db_session.session.add(url)
        db_session.session.commit()
        
        response = client.get('/api/v1/urls?page=1&per_page=10', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['urls']) == 10
        assert data['total'] == 25
        assert data['page'] == 1
        assert data['per_page'] == 10
    
    def test_search_urls(self, client, db_session, test_user, auth_headers):
        """Test URL search functionality."""
        # Create URLs with different titles
        url1 = URL(
            long_url='https://example1.com',
            short_code='code1',
            user_id=test_user.id,
            title='Marketing Campaign',
            description='Our main marketing page'
        )
        url2 = URL(
            long_url='https://example2.com',
            short_code='code2',
            user_id=test_user.id,
            title='Product Page',
            description='Product information'
        )
        db_session.session.add_all([url1, url2])
        db_session.session.commit()
        
        response = client.get('/api/v1/urls?search=marketing', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['urls']) == 1
        assert 'Marketing' in data['urls'][0]['title']
    
    def test_team_filtered_urls(self, client, db_session, test_user, test_team, auth_headers):
        """Test getting URLs filtered by team."""
        # Create URLs for different teams
        url1 = URL(
            long_url='https://team1.com',
            short_code='team1',
            user_id=test_user.id,
            team_id=test_team.id
        )
        url2 = URL(
            long_url='https://personal.com',
            short_code='pers1',
            user_id=test_user.id,
            team_id=None
        )
        db_session.session.add_all([url1, url2])
        db_session.session.commit()
        
        # Get team URLs
        response = client.get(f'/api/v1/urls?team_id={test_team.id}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['urls']) == 1
        assert data['urls'][0]['team_id'] == test_team.id
    
    def test_update_url(self, client, db_session, test_user, auth_headers):
        """Test URL update functionality."""
        url = URL(
            long_url='https://old.com',
            short_code='old',
            user_id=test_user.id,
            title='Old Title'
        )
        db_session.session.add(url)
        db_session.session.commit()
        
        response = client.put(f'/api/v1/urls/{url.short_code}', json={
            'title': 'New Title',
            'description': 'Updated description'
        }, headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['url']['title'] == 'New Title'
        assert data['url']['description'] == 'Updated description'
    
    def test_soft_delete_url(self, client, db_session, test_user, auth_headers):
        """Test soft delete functionality."""
        url = URL(
            long_url='https://delete.com',
            short_code='del',
            user_id=test_user.id
        )
        db_session.session.add(url)
        db_session.session.commit()
        
        response = client.delete(f'/api/v1/urls/{url.short_code}', headers=auth_headers)
        
        assert response.status_code == 200
        
        # Check that URL is soft deleted
        deleted_url = URL.query.get(url.id)
        assert deleted_url.is_active == False
    
    def test_enhanced_analytics(self, client, db_session, test_user, test_team, auth_headers):
        """Test enhanced analytics with team stats."""
        url = URL(
            long_url='https://analytics.com',
            short_code='anal',
            user_id=test_user.id,
            team_id=test_team.id,
            click_count=15
        )
        db_session.session.add(url)
        
        # Add another URL to the team for comparison
        url2 = URL(
            long_url='https://other.com',
            short_code='othr',
            user_id=test_user.id,
            team_id=test_team.id,
            click_count=25
        )
        db_session.session.add(url2)
        db_session.session.commit()
        
        response = client.get(f'/api/v1/analytics/{url.short_code}', headers=auth_headers)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['clicks'] == 15
        assert 'team_stats' in data
        assert data['team_stats']['total_urls'] == 2
        assert data['team_stats']['total_clicks'] == 40
    
    def test_admin_endpoints(self, client, db_session, test_user, auth_headers):
        """Test admin-only endpoints."""
        # Make user admin
        test_user.is_admin = True
        db_session.session.commit()
        
        response = client.get('/api/v1/admin/users', headers=auth_headers)
        assert response.status_code == 200
        
        response = client.get('/api/v1/admin/teams', headers=auth_headers)
        assert response.status_code == 200
    
    def test_non_admin_access_denied(self, client, db_session, test_user, auth_headers):
        """Test that non-admin users cannot access admin endpoints."""
        response = client.get('/api/v1/admin/users', headers=auth_headers)
        assert response.status_code == 403
    
    def test_team_member_required(self, client, db_session, test_user, auth_headers):
        """Test team membership requirement."""
        # Create team without adding user
        team = Team(name='Other Team')
        db_session.session.add(team)
        db_session.session.commit()
        
        response = client.get(f'/api/v1/teams/{team.id}', headers=auth_headers)
        assert response.status_code == 403
    
    def test_legacy_endpoint_compatibility(self, client, db_session):
        """Test legacy endpoint for backward compatibility."""
        # Create a URL without user (legacy style)
        url = URL(
            long_url='https://legacy.com',
            short_code='legacy',
            is_active=True
        )
        db_session.session.add(url)
        db_session.session.commit()
        
        response = client.get('/api/v1/urls/legacy')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['urls']) == 1
    
    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['version'] == '2.0.0'
