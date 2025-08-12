import pytest
import json
from datetime import datetime, timedelta
from app import create_app, db
from app.models import URL
from app.utils import generate_unique_short_code

@pytest.fixture
def app():
    """Create application for testing."""
    app = create_app('testing')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def sample_url():
    """Create a sample URL for testing."""
    return {
        'long_url': 'https://www.example.com/very/long/url/that/needs/shortening',
        'expires_at': (datetime.utcnow() + timedelta(days=30)).isoformat()
    }

class TestURLShortening:
    """Test URL shortening functionality."""
    
    def test_shorten_url_success(self, client, sample_url):
        """Test successful URL shortening."""
        response = client.post('/shorten',
                             data=json.dumps({'long_url': sample_url['long_url']}),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'short_url' in data
        assert 'http://localhost:5000/' in data['short_url']
    
    def test_shorten_url_with_expiration(self, client, sample_url):
        """Test URL shortening with expiration date."""
        response = client.post('/shorten',
                             data=json.dumps(sample_url),
                             content_type='application/json')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'short_url' in data
    
    def test_shorten_duplicate_url(self, client, sample_url):
        """Test that duplicate URLs return the same short code."""
        # First request
        response1 = client.post('/shorten',
                              data=json.dumps({'long_url': sample_url['long_url']}),
                              content_type='application/json')
        
        # Second request with same URL
        response2 = client.post('/shorten',
                              data=json.dumps({'long_url': sample_url['long_url']}),
                              content_type='application/json')
        
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        data1 = json.loads(response1.data)
        data2 = json.loads(response2.data)
        assert data1['short_url'] == data2['short_url']
    
    def test_shorten_invalid_url(self, client):
        """Test shortening with invalid URL."""
        response = client.post('/shorten',
                             data=json.dumps({'long_url': 'not-a-valid-url'}),
                             content_type='application/json')
        
        assert response.status_code == 422

class TestURLRedirect:
    """Test URL redirection functionality."""
    
    def test_redirect_success(self, client, app, sample_url):
        """Test successful URL redirection."""
        with app.app_context():
            # Create a URL in the database
            url_obj = URL(
                long_url=sample_url['long_url'],
                short_code='test123'
            )
            db.session.add(url_obj)
            db.session.commit()
            
            # Test redirect
            response = client.get('/test123', follow_redirects=False)
            assert response.status_code == 302
            assert response.location == sample_url['long_url']
    
    def test_redirect_nonexistent_url(self, client):
        """Test redirect with non-existent short code."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
    
    def test_redirect_expired_url(self, client, app, sample_url):
        """Test redirect with expired URL."""
        with app.app_context():
            # Create an expired URL
            url_obj = URL(
                long_url=sample_url['long_url'],
                short_code='expired',
                expires_at=datetime.utcnow() - timedelta(days=1)
            )
            db.session.add(url_obj)
            db.session.commit()
            
            # Test redirect
            response = client.get('/expired')
            assert response.status_code == 410

class TestCRUDOperations:
    """Test CRUD operations."""
    
    def test_get_all_urls(self, client, app, sample_url):
        """Test getting all URLs."""
        with app.app_context():
            # Create some URLs
            url1 = URL(long_url='https://example1.com', short_code='abc123')
            url2 = URL(long_url='https://example2.com', short_code='def456')
            db.session.add_all([url1, url2])
            db.session.commit()
            
            response = client.get('/urls')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data['urls']) == 2
            assert data['total'] == 2
    
    def test_get_specific_url(self, client, app, sample_url):
        """Test getting a specific URL."""
        with app.app_context():
            url_obj = URL(long_url=sample_url['long_url'], short_code='test123')
            db.session.add(url_obj)
            db.session.commit()
            
            response = client.get('/urls/test123')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['short_code'] == 'test123'
            assert data['long_url'] == sample_url['long_url']
    
    def test_update_url(self, client, app, sample_url):
        """Test updating a URL."""
        with app.app_context():
            url_obj = URL(long_url=sample_url['long_url'], short_code='test123')
            db.session.add(url_obj)
            db.session.commit()
            
            new_url = 'https://www.newexample.com'
            response = client.put('/urls/test123',
                                data=json.dumps({'long_url': new_url}),
                                content_type='application/json')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['long_url'] == new_url
    
    def test_delete_url(self, client, app, sample_url):
        """Test deleting a URL."""
        with app.app_context():
            url_obj = URL(long_url=sample_url['long_url'], short_code='test123')
            db.session.add(url_obj)
            db.session.commit()
            
            response = client.delete('/urls/test123')
            assert response.status_code == 200
            
            # Verify it's deleted
            get_response = client.get('/urls/test123')
            assert get_response.status_code == 404

class TestAnalytics:
    """Test analytics functionality."""
    
    def test_get_analytics(self, client, app, sample_url):
        """Test getting analytics for a URL."""
        with app.app_context():
            url_obj = URL(long_url=sample_url['long_url'], short_code='test123')
            db.session.add(url_obj)
            db.session.commit()
            
            # Simulate some clicks
            url_obj.click_count = 5
            db.session.commit()
            
            response = client.get('/analytics/test123')
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['short_code'] == 'test123'
            assert data['clicks'] == 5
    
    def test_analytics_nonexistent_url(self, client):
        """Test analytics for non-existent URL."""
        response = client.get('/analytics/nonexistent')
        assert response.status_code == 404

class TestUtils:
    """Test utility functions."""
    
    def test_generate_unique_short_code(self, app):
        """Test short code generation."""
        with app.app_context():
            code1 = generate_unique_short_code()
            code2 = generate_unique_short_code()
            
            assert len(code1) == 6
            assert len(code2) == 6
            assert code1 != code2
            assert code1.isalnum()
            assert code2.isalnum()
